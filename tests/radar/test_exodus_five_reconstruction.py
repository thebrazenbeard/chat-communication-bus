import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOPOLOGY = ROOT / "architecture/contracts/RADAR_TOPOLOGY_V1.json"
CENSUS = ROOT / "architecture/contracts/EXODUS_WORKER_RECONSTRUCTION_CENSUS_V1.json"
FIVE = ROOT / "architecture/reconstruction/EXODUS_WORKER_FIVE_V1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_five_reconstruction_is_chatless_and_routes_to_current_v2_lane():
    topology = load(TOPOLOGY)
    five = load(FIVE)

    assert five["identity_id"] == "five"
    assert five["reconstruction_status"] == "READY"
    assert five["retired_chat_required"] is False
    assert topology["required_writer_lanes"]["five"]["lifecycle"] == "ACTIVE"
    assert topology["required_writer_lanes"]["five"]["branch"] == "bus/five-v2"
    assert five["bus_route"]["current_branch"] == "bus/five-v2"
    assert five["bus_route"]["legacy_branch"]["branch"] == "bus/five-v1"
    assert (
        five["bus_route"]["legacy_branch"]["classification"]
        == "HISTORICAL_PROVENANCE_ONLY_NOT_CURRENT_WRITE_ROUTE"
    )


def test_five_has_no_chat_derived_assignment_after_retirement():
    five = load(FIVE)

    assert (
        five["current_assignment_frontier"]["mode"]
        == "IDLE_NO_CURRENT_ASSIGNMENT_ESTABLISHED"
    )
    assert five["current_assignment_frontier"]["current_route_assignment_found"] is False
    assert "retired chat" in five["current_assignment_frontier"]["rule"].lower()


def test_five_ready_census_entry_matches_reconstruction_route_head():
    five = load(FIVE)
    census = load(CENSUS)
    entry = next(item for item in census["workers"] if item["identity_id"] == "five")

    assert entry["reconstruction_status"] == "READY"
    assert entry["missing_reconstruction_fields"] == []
    assert entry["observed_head"] == five["bus_route"]["observed_head"]
    assert "architecture/reconstruction/EXODUS_WORKER_FIVE_V1.json" in entry["durable_evidence"]

    ready = [item for item in census["workers"] if item["reconstruction_status"] == "READY"]
    assert census["census_cut"]["qualified_worker_count"] == len(ready)
    assert census["census_cut"]["unqualified_worker_count"] == (
        census["census_cut"]["active_writer_count"] - len(ready)
    )
    assert census["cutover_gate"]["status"] == "BLOCKED"
