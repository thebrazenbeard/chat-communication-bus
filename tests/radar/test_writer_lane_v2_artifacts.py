import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _topology():
    return json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json").read_text(encoding="utf-8")
    )


def _cutover():
    return json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_WRITER_LANE_V2_CUTOVER.json").read_text(encoding="utf-8")
    )


def test_source_readiness_pr_does_not_switch_current_topology_before_successors_exist():
    lanes = _topology()["required_writer_lanes"]
    assert lanes["radar"]["branch"] == "bus/radar-v1"
    assert lanes["brigit"]["branch"] == "bus/bridget-v1"
    assert lanes["one"]["branch"] == "bus/one-v1"
    assert lanes["hephaestus"]["branch"] == "bus/hephaestus-v2"
    assert lanes["vera"]["branch"] == "bus/vera-sol-v1"


def test_cutover_contract_covers_current_fleet_without_pretending_it_is_historical_yet():
    topology = _topology()
    cutover = _cutover()
    assert cutover["status"] == "PRE_MERGE_PLANNED"
    assert cutover["cutover_main_sha"] is None
    assert set(cutover["historical_writer_lanes"]) == set(topology["required_writer_lanes"])
    for identity, record in topology["required_writer_lanes"].items():
        predecessor = cutover["historical_writer_lanes"][identity]
        assert predecessor["branch"] == record["branch"]
        assert predecessor["head_sha"] is None
    assert cutover["protected_effects"] == {
        "merge": False,
        "provider_cutover": False,
        "ruleset_change": False,
    }


def test_cutover_contract_declares_successors_without_claiming_creation_or_switch():
    cutover = _cutover()
    assert cutover["planned_current_writer_lanes"]["radar"] == "bus/radar-v2"
    assert cutover["planned_current_writer_lanes"]["brigit"] == "bus/brigit-v2"
    assert cutover["planned_current_writer_lanes"]["hephaestus"] == "bus/hephaestus-v3"
    assert cutover["planned_current_writer_lanes"]["vera"] == "bus/vera-v2"
    assert cutover["successor_branches_created"] is False
    assert cutover["topology_switched"] is False


def test_cutover_sequence_requires_branch_creation_before_topology_switch():
    cutover = _cutover()
    assert cutover["sequence"] == [
        "MERGE_SOURCE_READINESS",
        "SNAPSHOT_PREDECESSOR_HEADS",
        "CREATE_SUCCESSOR_BRANCHES_FROM_EXACT_MAIN",
        "VERIFY_SUCCESSOR_BRANCHES",
        "MERGE_TOPOLOGY_SWITCH",
        "ROUTE_NEW_MESSAGES_TO_SUCCESSORS",
    ]
