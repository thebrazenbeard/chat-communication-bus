from __future__ import annotations

from radar.envelope import RadarEnvelope
from radar.model import NodeStatus
from radar.registry import IdentityRegistry
from radar.routing import Router


def _env() -> RadarEnvelope:
    result = RadarEnvelope.from_mapping(
        {
            "schema_version": 1,
            "message_id": "radar-multi-audience-snapshot-0001",
            "created_at": "2026-09-06T14:15:00Z",
            "sender": "radar",
            "audience": ["yin", "yang"],
            "domain": "database",
            "intent": "event",
            "priority": 2,
            "payload": {"snapshot": "multi-audience"},
        }
    )
    assert result.envelope is not None
    return result.envelope


def test_multi_audience_route_uses_one_registry_eligibility_snapshot():
    class CountingRegistry(IdentityRegistry):
        def __init__(self):
            super().__init__()
            self.snapshot_calls = []

        def routable_subscriber_node_ids(self, *args, **kwargs):
            self.snapshot_calls.append(dict(kwargs))
            return super().routable_subscriber_node_ids(*args, **kwargs)

    registry = CountingRegistry()
    for identity in ("yin", "yang"):
        registry.register_identity(identity, display_name=identity.title())
        registry.register_node(
            f"{identity}-node",
            identity_id=identity,
            status=NodeStatus.ONLINE,
            last_heartbeat_ms=1_000,
            lease_expires_ms=2_000,
        )
        registry.subscribe(
            f"{identity}-node",
            domain="database",
            intent="event",
            min_priority=4,
        )

    decision = Router(registry).route(_env(), now_ms=1_500)

    assert decision.recipients == ("yin-node", "yang-node")
    assert len(registry.snapshot_calls) == 1
    assert registry.snapshot_calls[0]["identity_ids"] == ("yin", "yang")
