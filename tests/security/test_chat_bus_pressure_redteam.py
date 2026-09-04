from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

from radar.envelope import EnvelopeClassification, RadarEnvelope
from radar.routing import DedupeWindow, PriorityQueue
from radar.writer_lanes import WriterLaneError, validate_writer_lane_commit


ROOT = Path(__file__).resolve().parents[2]
EMITTER_SCRIPT = ROOT / "scripts" / "radar_emit_bus_projection.py"
EDGE_HANDLER = ROOT / "supabase" / "functions" / "github-bus-ingest" / "handler.ts"
CURRENT_REF = "refs/heads/bus/one-v2"


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def make_lane_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "lane"
    repo.mkdir()
    subprocess.check_call(["git", "-C", str(repo), "init", "-q"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.email", "pressure@example.com"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.name", "Pressure Test"])
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
    spec = importlib.util.spec_from_file_location("radar_emit_bus_projection_pressure", EMITTER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def envelope(*, priority: int, idempotency_key: str | None = None) -> RadarEnvelope:
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


def test_unrecognized_domain_and_intent_fail_closed_at_envelope_boundary():
    result = RadarEnvelope.from_mapping(
        {
            "schema_version": 1,
            "sender": "radar",
            "domain": "__not_registered_domain__",
            "intent": "__not_registered_intent__",
            "payload": {"attack": "taxonomy-bypass"},
        }
    )

    assert result.classification is EnvelopeClassification.REJECTED


def test_caller_cannot_bypass_deterministic_500ms_dedupe_with_custom_key():
    first = envelope(priority=3, idempotency_key="attacker-key-a")
    second = envelope(priority=3, idempotency_key="attacker-key-b")
    assert first.content_hash == second.content_hash

    window = DedupeWindow(window_ms=500)
    assert window.accept(first.idempotency_key, 1_000) is True
    assert window.accept(second.idempotency_key, 1_100) is False


def test_priority_zero_is_not_blocked_by_background_queue_saturation():
    queue = PriorityQueue(max_size=2)
    queue.push(envelope(priority=4, idempotency_key="bg-1"))
    queue.push(envelope(priority=4, idempotency_key="bg-2"))

    queue.push(envelope(priority=0, idempotency_key="halt"))

    assert queue.pop().priority == 0


def test_writer_lane_rejects_message_missing_writer_before_projection(tmp_path):
    repo, base = make_lane_repo(tmp_path)
    topology = write_topology(tmp_path)
    head = commit_message(
        repo,
        "missing-writer.md",
        "# One -> Radar\n\nmessage_id: one-pressure-0001\n\nhello\n",
    )

    with pytest.raises(WriterLaneError):
        validate_writer_lane_commit(repo, CURRENT_REF, head, topology, base=base)


def test_writer_lane_rejects_message_missing_message_id_before_projection(tmp_path):
    repo, base = make_lane_repo(tmp_path)
    topology = write_topology(tmp_path)
    head = commit_message(
        repo,
        "missing-id.md",
        "# One -> Radar\n\nwriter: One\n\nhello\n",
    )

    with pytest.raises(WriterLaneError):
        validate_writer_lane_commit(repo, CURRENT_REF, head, topology, base=base)


def test_full_mailbox_projection_stays_inside_edge_500_file_limit(tmp_path):
    emitter = load_emitter()
    repo, base = make_lane_repo(tmp_path)
    topology = write_topology(tmp_path)

    for index in range(501):
        path = repo / "messages" / f"{index:04d}.md"
        path.write_text(
            "# One -> Radar\n\n"
            f"message_id: one-pressure-{index:04d}\n"
            "writer: One\n"
            "created_at: 2026-09-04T20:00:00Z\n\n"
            "load\n",
            encoding="utf-8",
        )
    subprocess.check_call(["git", "-C", str(repo), "add", "messages"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "501-message pressure fixture"])
    head = git(repo, "rev-parse", "HEAD")

    batch = emitter.collect_projection_batch(
        repo,
        repository="thebrazenbeard/chat-communication-bus",
        ref=CURRENT_REF,
        branch_head=head,
        base_commit=base,
        topology_path=topology,
    )

    assert len(batch["files"]) <= 500


def test_edge_authentication_is_bound_to_trusted_reusable_workflow_not_branch_copy():
    source = EDGE_HANDLER.read_text(encoding="utf-8")

    assert 'stringClaim(claims, "job_workflow_ref")' in source


def test_edge_sender_identity_is_derived_from_admitted_lane_not_message_bytes():
    source = EDGE_HANDLER.read_text(encoding="utf-8")

    assert "p_sender: writer" not in source
    assert "lane_identity" in source
