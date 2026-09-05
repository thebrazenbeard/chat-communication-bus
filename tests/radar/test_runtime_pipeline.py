from __future__ import annotations

from radar.dlq import DeadLetterStore
from radar.registry import IdentityRegistry
from radar.runtime import RadarRuntime
from radar.telemetry import TelemetryStore


def _registry() -> IdentityRegistry:
    registry = IdentityRegistry()
    for identity in ("one", "two"):
        registry.register_identity(identity, display_name=identity.title())
        registry.register_node(f"{identity}-node", identity_id=identity)
        registry.subscribe(identity, domain="database", min_priority=4)
        registry.subscribe(identity, domain="system", min_priority=4)
    return registry


def _raw(
    message_id: str,
    *,
    audience=("one",),
    domain="database",
    intent="event",
    priority=3,
    payload=None,
):
    return {
        "schema_version": 1,
        "message_id": message_id,
        "created_at": "2026-09-05T21:20:00Z",
        "sender": "radar",
        "audience": list(audience),
        "domain": domain,
        "intent": intent,
        "priority": priority,
        "payload": {"value": 1} if payload is None else payload,
    }


def _runtime(tmp_path, *, queue_size=8) -> RadarRuntime:
    return RadarRuntime(
        _registry(),
        telemetry=TelemetryStore(tmp_path / "telemetry.sqlite"),
        dlq=DeadLetterStore(tmp_path / "dlq.sqlite"),
        queue_size=queue_size,
    )


def test_unknown_taxonomy_is_durably_dlq_accounted(tmp_path):
    runtime = _runtime(tmp_path)

    receipt = runtime.admit(
        _raw("radar-unknown-0001", domain="not-a-domain"),
        now_ms=1_000,
        source_locator="bus/radar-v2@abc:messages/radar-unknown-0001.md",
    )

    assert receipt.state == "DLQ"
    assert receipt.message_id == "radar-unknown-0001"
    assert receipt.dlq_item_id is not None
    item = runtime.dlq.inspect(receipt.dlq_item_id)
    assert item.failure_stage == "ADMISSION"
    assert item.failure_code == "UNKNOWN_TAXONOMY"
    assert item.reason_category == "TAXONOMY"
    assert item.source_locator == "bus/radar-v2@abc:messages/radar-unknown-0001.md"
    assert runtime.telemetry.snapshot().as_dict() == {
        "routed": 0,
        "dropped": 0,
        "dlq": 1,
    }


def test_unknown_taxonomy_with_unserializable_payload_still_reaches_durable_dlq(tmp_path):
    runtime = _runtime(tmp_path)
    opaque_payload = object()

    receipt = runtime.admit(
        _raw("radar-unknown-opaque-0001", domain="not-a-domain", payload=opaque_payload),
        now_ms=1_500,
        source_locator="bus/radar-v2@def:messages/radar-unknown-opaque-0001.md",
    )

    assert receipt.state == "DLQ"
    assert receipt.dlq_item_id is not None
    item = runtime.dlq.inspect(receipt.dlq_item_id)
    assert item.message_id == "radar-unknown-opaque-0001"
    assert item.failure_code == "UNKNOWN_TAXONOMY"
    assert item.envelope["payload"] == "<object>"
    assert runtime.telemetry.snapshot().dlq == 1


def test_dedupe_is_scoped_to_route_context_not_payload_globally(tmp_path):
    runtime = _runtime(tmp_path)
    payload = {"same": "payload"}

    first = runtime.admit(
        _raw("radar-route-0001", audience=("one",), payload=payload), now_ms=10_000
    )
    duplicate = runtime.admit(
        _raw("radar-route-0002", audience=("one",), payload=payload), now_ms=10_100
    )
    other_route = runtime.admit(
        _raw("radar-route-0003", audience=("two",), payload=payload), now_ms=10_200
    )

    assert first.state == "QUEUED"
    assert duplicate.state == "DROPPED_DUPLICATE"
    assert other_route.state == "QUEUED"
    assert runtime.telemetry.snapshot().dropped == 1


def test_priority_zero_evicts_background_counts_drop_and_dispatches_immediately(tmp_path):
    runtime = _runtime(tmp_path, queue_size=2)

    assert runtime.admit(
        _raw("radar-bg-0001", priority=4, domain="system", intent="telemetry"),
        now_ms=20_000,
    ).state == "QUEUED"
    assert runtime.admit(
        _raw("radar-bg-0002", priority=4, domain="system", intent="telemetry", payload={"n": 2}),
        now_ms=20_600,
    ).state == "QUEUED"

    urgent = runtime.admit(
        _raw("radar-halt-0001", priority=0, domain="system", intent="command", payload={"halt": True}),
        now_ms=21_200,
    )

    assert urgent.state == "DISPATCHED"
    assert urgent.recipients == ("one",)
    assert urgent.evicted_message_id == "radar-bg-0002"
    assert runtime.telemetry.snapshot().as_dict() == {
        "routed": 1,
        "dropped": 1,
        "dlq": 0,
    }


def test_normal_dispatch_accounts_one_routed_message_not_recipient_fanout(tmp_path):
    runtime = _runtime(tmp_path)
    queued = runtime.admit(
        _raw("radar-fanout-0001", audience=(), payload={"fanout": True}),
        now_ms=30_000,
    )
    assert queued.state == "QUEUED"

    dispatched = runtime.dispatch_next()

    assert dispatched.state == "DISPATCHED"
    assert dispatched.recipients == ("one", "two")
    assert runtime.telemetry.snapshot().routed == 1
