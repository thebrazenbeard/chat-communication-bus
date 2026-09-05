from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

from radar.envelope import EnvelopeClassification, RadarEnvelope
from radar.model import NodeStatus
from radar.registry import IdentityRegistry
from radar.routing import DedupeWindow, PriorityQueue, Router
from radar.writer_lanes import WriterLaneError, validate_writer_lane_commit


ROOT = Path(__file__).resolve().parents[2]
EMITTER_SCRIPT = ROOT / "scripts" / "radar_emit_bus_projection.py"
CURRENT_REF = "refs/heads/bus/one-v2"


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def make_lane_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "lane"
    repo.mkdir()
    subprocess.check_call(["git", "-C", str(repo), "init", "-q"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.email", "hardening@example.com"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.name", "Hardening Test"])
    (repo / "messages").mkdir()
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.check_call(["git", "-C", str(repo), "add", "."])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "base"])
    return repo, git(repo, "rev-parse", "HEAD")


def write_topology(tmp_path: Path) -> Path:
    topology = tmp_path / "topology.json"
    topology.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "required_writer_lanes": {
                    "one": {
                        "writer": "One",
                        "branch": "bus/one-v2",
                        "legacy_spelling": False,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return topology


def commit_message(repo: Path, name: str, content: str) -> str:
    path = repo / "messages" / name
    path.write_text(content, encoding="utf-8")
    subprocess.check_call(["git", "-C", str(repo), "add", str(path.relative_to(repo))])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", f"add {name}"])
    return git(repo, "rev-parse", "HEAD")


def load_emitter():
    spec = importlib.util.spec_from_file_location("radar_emit_bus_projection_hardening", EMITTER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def envelope(*, priority: int = 3, idempotency_key: str | None = None) -> RadarEnvelope:
    raw: dict[str, object] = {
        "schema_version": 1,
        "message_id": f"pressure-{priority}-{idempotency_key or 'default'}",
        "created_at": "2026-09-04T20:00:00Z",
        "sender": "radar",
        "audience": ["one"],
        "domain": "system",
        "intent": "event",
        "priority": priority,
        "payload": {"same": "payload"},
    }
    if idempotency_key is not None:
        raw["idempotency_key"] = idempotency_key
    result = RadarEnvelope.from_mapping(raw)
    assert result.envelope is not None
    return result.envelope


def routed_envelope(*, audience: list[str], domain: str = "database", priority: int = 3) -> RadarEnvelope:
    result = RadarEnvelope.from_mapping(
        {
            "schema_version": 1,
            "message_id": "pressure-route-0001",
            "created_at": "2026-09-04T20:00:00Z",
            "sender": "radar",
            "audience": audience,
            "domain": domain,
            "intent": "event",
            "priority": priority,
            "payload": {"pressure": "routing"},
        }
    )
    assert result.envelope is not None
    return result.envelope


def register_routable(registry: IdentityRegistry, identity: str, *, domain: str = "database") -> None:
    registry.register_identity(identity, display_name=identity.title())
    registry.register_node(f"{identity}-node", identity_id=identity, status=NodeStatus.ONLINE)
    registry.subscribe(identity, domain=domain, min_priority=4)


def test_unrecognized_domain_or_intent_goes_to_dlq():
    bad_domain = RadarEnvelope.from_mapping(
        {
            "schema_version": 1,
            "sender": "radar",
            "domain": "__not_registered_domain__",
            "intent": "event",
            "payload": {},
        }
    )
    bad_intent = RadarEnvelope.from_mapping(
        {
            "schema_version": 1,
            "sender": "radar",
            "domain": "system",
            "intent": "__not_registered_intent__",
            "payload": {},
        }
    )

    assert bad_domain.classification is EnvelopeClassification.DLQ
    assert bad_intent.classification is EnvelopeClassification.DLQ
    assert "domain" in bad_domain.errors
    assert "intent" in bad_intent.errors


def test_caller_selected_idempotency_key_cannot_bypass_deterministic_dedupe():
    first = envelope(idempotency_key="attacker-key-a")
    second = envelope(idempotency_key="attacker-key-b")
    assert first.content_hash == second.content_hash
    assert first.idempotency_key == second.idempotency_key
    assert first.idempotency_key != first.content_hash

    window = DedupeWindow(window_ms=500)
    assert window.accept(first.idempotency_key, 1_000) is True
    assert window.accept(second.idempotency_key, 1_100) is False


def test_priority_zero_evicts_background_item_when_queue_is_full():
    queue = PriorityQueue(max_size=2)
    queue.push(envelope(priority=4, idempotency_key="bg-1"))
    queue.push(envelope(priority=4, idempotency_key="bg-2"))

    queue.push(envelope(priority=0, idempotency_key="halt"))

    assert len(queue) == 2
    assert queue.pop().priority == 0


def test_priority_zero_does_not_silently_evict_priority_zero():
    queue = PriorityQueue(max_size=1)
    queue.push(envelope(priority=0, idempotency_key="halt-1"))
    with pytest.raises(OverflowError, match="RADAR_QUEUE_FULL"):
        queue.push(envelope(priority=0, idempotency_key="halt-2"))


def test_explicit_audience_requires_matching_subscription_and_routable_node():
    registry = IdentityRegistry()
    register_routable(registry, "one")
    registry.register_identity("two", display_name="Two")
    registry.register_node("two-node", identity_id="two", status=NodeStatus.ONLINE)

    decision = Router(registry).route(routed_envelope(audience=["two"]))

    assert decision.recipients == ()


def test_explicit_audience_routes_when_subscription_and_node_are_valid():
    registry = IdentityRegistry()
    register_routable(registry, "one")

    decision = Router(registry).route(routed_envelope(audience=["one"]))

    assert decision.recipients == ("one",)


def test_offline_identity_is_not_routed_subscription_or_direct_traffic():
    registry = IdentityRegistry()
    registry.register_identity("one", display_name="One")
    registry.register_node("one-node", identity_id="one", status=NodeStatus.OFFLINE)
    registry.subscribe("one", domain="database", min_priority=4)

    assert Router(registry).route(routed_envelope(audience=[])).recipients == ()
    assert Router(registry).route(routed_envelope(audience=["one"])).recipients == ()


def test_writer_lane_requires_top_level_writer_header(tmp_path):
    repo, base = make_lane_repo(tmp_path)
    topology = write_topology(tmp_path)
    head = commit_message(
        repo,
        "missing-writer.md",
        "# One -> Radar\n\nmessage_id: one-pressure-0001\n\nhello\n",
    )

    with pytest.raises(WriterLaneError, match="WRITER_LANE_WRITER_REQUIRED"):
        validate_writer_lane_commit(repo, CURRENT_REF, head, topology, base=base)


def test_writer_lane_requires_top_level_message_id_header(tmp_path):
    repo, base = make_lane_repo(tmp_path)
    topology = write_topology(tmp_path)
    head = commit_message(
        repo,
        "missing-id.md",
        "# One -> Radar\n\nwriter: One\n\nhello\n",
    )

    with pytest.raises(WriterLaneError, match="WRITER_LANE_MESSAGE_ID_REQUIRED"):
        validate_writer_lane_commit(repo, CURRENT_REF, head, topology, base=base)


def test_body_only_writer_marker_does_not_satisfy_writer_guard(tmp_path):
    repo, base = make_lane_repo(tmp_path)
    topology = write_topology(tmp_path)
    head = commit_message(
        repo,
        "body-writer.md",
        "# One -> Radar\n\n"
        "message_id: one-pressure-0002\n"
        "created_at: 2026-09-04T20:00:00Z\n\n"
        "payload starts here\n"
        "writer: One\n",
    )

    with pytest.raises(WriterLaneError, match="WRITER_LANE_WRITER_REQUIRED"):
        validate_writer_lane_commit(repo, CURRENT_REF, head, topology, base=base)


def test_writer_lane_rejects_foreign_identity_message_id_namespace(tmp_path):
    repo, base = make_lane_repo(tmp_path)
    topology = write_topology(tmp_path)
    head = commit_message(
        repo,
        "foreign-id.md",
        "# One -> Radar\n\n"
        "message_id: radar-pressure-9999\n"
        "writer: One\n"
        "created_at: 2026-09-04T20:00:00Z\n\n"
        "namespace collision attempt\n",
    )

    with pytest.raises(WriterLaneError, match="WRITER_LANE_MESSAGE_ID_NAMESPACE"):
        validate_writer_lane_commit(repo, CURRENT_REF, head, topology, base=base)


def test_projection_conflict_causes_emitter_nonzero_exit(monkeypatch, tmp_path):
    emitter = load_emitter()
    topology = write_topology(tmp_path)
    cutover = tmp_path / "cutover.json"
    cutover.write_text(
        json.dumps({"planned_current_writer_lanes": {"one": "bus/one-v2"}}),
        encoding="utf-8",
    )

    monkeypatch.setattr(emitter, "planned_successor_bootstrap_identity", lambda *args, **kwargs: None)
    monkeypatch.setattr(emitter, "collect_projection_batch", lambda *args, **kwargs: {"files": []})
    monkeypatch.setattr(emitter, "request_oidc_token", lambda *args, **kwargs: "test-token")
    monkeypatch.setattr(
        emitter,
        "post_projection_batch",
        lambda *args, **kwargs: {
            "ok": True,
            "results": [{"path": "messages/conflict.md", "result": "CONFLICT"}],
        },
    )

    exit_code = emitter.main(
        [
            "--repo-dir",
            str(tmp_path),
            "--repository",
            "thebrazenbeard/chat-communication-bus",
            "--ref",
            CURRENT_REF,
            "--head",
            "1" * 40,
            "--base",
            "2" * 40,
            "--topology",
            str(topology),
            "--cutover",
            str(cutover),
        ]
    )

    assert exit_code != 0
