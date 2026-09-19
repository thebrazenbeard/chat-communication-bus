import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOPOLOGY = ROOT / "architecture/contracts/RADAR_TOPOLOGY_V1.json"
EXODUS = ROOT / "architecture/contracts/EXODUS_INTERFACE_TOPOLOGY_V1.json"
CENSUS = ROOT / "architecture/contracts/EXODUS_WORKER_RECONSTRUCTION_CENSUS_V1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_reconstruction_census_exactly_covers_active_writer_topology():
    topology = load(TOPOLOGY)
    census = load(CENSUS)
    active = {
        (identity_id, item["writer"], item["branch"])
        for identity_id, item in topology["required_writer_lanes"].items()
        if item["lifecycle"] == "ACTIVE"
    }
    observed = {
        (item["identity_id"], item["writer"], item["branch"])
        for item in census["workers"]
    }
    assert census["census_cut"]["active_writer_count"] == len(active)
    assert observed == active


def test_every_census_worker_pins_exact_observed_head_and_status():
    census = load(CENSUS)
    for worker in census["workers"]:
        assert len(worker["observed_head"]) == 40
        int(worker["observed_head"], 16)
        assert worker["reconstruction_status"] in {"NOT_QUALIFIED", "READY"}
        assert isinstance(worker["missing_reconstruction_fields"], list)


def test_chat_retirement_remains_blocked_until_all_active_workers_ready():
    exodus = load(EXODUS)
    census = load(CENSUS)
    ready = [
        worker for worker in census["workers"]
        if worker["reconstruction_status"] == "READY"
    ]
    assert census["census_cut"]["qualified_worker_count"] == len(ready)
    assert census["census_cut"]["unqualified_worker_count"] == (
        census["census_cut"]["active_writer_count"] - len(ready)
    )
    assert census["cutover_gate"]["status"] == "BLOCKED"
    assert exodus["chat_retirement_gate"]["status"] == "BLOCKED"
    assert (
        exodus["worker_reconstruction_census"]["required_for_worker_chat_retirement"]
        is True
    )


def test_branch_existence_is_not_reconstruction_proof():
    census = load(CENSUS)
    assert census["workers"]
    ready = [
        worker for worker in census["workers"]
        if worker["reconstruction_status"] == "READY"
    ]
    unqualified = [
        worker for worker in census["workers"]
        if worker["reconstruction_status"] == "NOT_QUALIFIED"
    ]
    assert ready
    assert unqualified
    assert all(not worker["missing_reconstruction_fields"] for worker in ready)
    assert all(worker["missing_reconstruction_fields"] for worker in unqualified)
    assert census["census_cut"]["qualified_worker_count"] == len(ready)
    assert census["census_cut"]["unqualified_worker_count"] == len(unqualified)
    assert census["cutover_gate"]["status"] == "BLOCKED"
