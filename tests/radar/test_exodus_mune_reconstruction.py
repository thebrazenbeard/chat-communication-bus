import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MUNE = ROOT / "architecture/reconstruction/EXODUS_WORKER_MUNE_V1.json"


def load():
    return json.loads(MUNE.read_text(encoding="utf-8"))


def test_mune_reconstruction_is_chatless_and_topology_routed():
    record = load()
    assert record["identity_id"] == "mune"
    assert record["reconstruction_status"] == "READY"
    assert record["retired_chat_required"] is False
    assert record["bus_route"]["branch"] == "bus/mune-v2"
    assert record["current_assignment_frontier"]["status"] == "NONE_ASSERTED_BY_RECONSTRUCTION_RECORD"


def test_mune_reconstruction_binds_canonical_bt2_v101_package():
    record = load()
    bt2 = record["repositories"]["build_team_two"]
    assert bt2["repo"] == "thebrazenbeard/bt2"
    assert bt2["source_path"] == "archive/training-sources/build-team-2.0/mune/v1.0.1"
    assert bt2["package_tree"] == "5e8c87021bfda9a6fc44fa121c32410ddc6aedf9"
    assert bt2["manifest_blob"] == "5d2b6cdaa603b60edc860801eaae5dd8644d3c9a"


def test_mune_source_presence_does_not_self_award_qualification():
    record = load()
    gap = record["qualification_gap"].casefold()
    assert "not established" in gap
    assert "base_ready" in gap
    assert record["current_vs_historical_state"]["qualification_is_not_installation"] is True


def test_mune_recovery_requires_no_conversation_locator():
    record = load()
    serialized = json.dumps(record).casefold()
    assert "chatgpt-conversation://" not in serialized
    assert "thread://" not in serialized
    assert any("mune_exodus_final_20260920t0713-0400" in item.casefold() for item in record["durable_evidence"])
