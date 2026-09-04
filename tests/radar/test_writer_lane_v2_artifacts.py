import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_topology_uses_clean_current_writer_lane_generations():
    topology = json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json").read_text(encoding="utf-8")
    )
    lanes = topology["required_writer_lanes"]
    assert lanes["radar"]["branch"] == "bus/radar-v2"
    assert lanes["brigit"]["branch"] == "bus/brigit-v2"
    assert lanes["one"]["branch"] == "bus/one-v2"
    assert lanes["hephaestus"]["branch"] == "bus/hephaestus-v3"
    assert len({record["branch"] for record in lanes.values()}) == len(lanes)
    assert all(record["branch"].endswith(("-v2", "-v3")) for record in lanes.values())


def test_topology_preserves_historical_branch_address_for_every_identity():
    topology = json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json").read_text(encoding="utf-8")
    )
    lanes = topology["required_writer_lanes"]
    assert all(record.get("historical_branch") for record in lanes.values())
    assert lanes["radar"]["historical_branch"] == "bus/radar-v1"
    assert lanes["brigit"]["historical_branch"] == "bus/bridget-v1"
    assert lanes["hephaestus"]["historical_branch"] == "bus/hephaestus-v2"


def test_cutover_contract_is_truthful_pre_merge_and_covers_full_fleet():
    topology = json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json").read_text(encoding="utf-8")
    )
    cutover = json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_WRITER_LANE_V2_CUTOVER.json").read_text(encoding="utf-8")
    )
    assert cutover["status"] == "PRE_MERGE_PLANNED"
    assert cutover["cutover_main_sha"] is None
    assert set(cutover["historical_writer_lanes"]) == set(topology["required_writer_lanes"])
    for identity, record in topology["required_writer_lanes"].items():
        historical = cutover["historical_writer_lanes"][identity]
        assert historical["branch"] == record["historical_branch"]
        assert historical["head_sha"] is None
    assert cutover["protected_effects"] == {
        "merge": False,
        "provider_cutover": False,
        "ruleset_change": False,
    }


def test_cutover_contract_declares_planned_current_lane_without_claiming_creation():
    cutover = json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_WRITER_LANE_V2_CUTOVER.json").read_text(encoding="utf-8")
    )
    assert cutover["planned_current_writer_lanes"]["radar"] == "bus/radar-v2"
    assert cutover["planned_current_writer_lanes"]["brigit"] == "bus/brigit-v2"
    assert cutover["planned_current_writer_lanes"]["hephaestus"] == "bus/hephaestus-v3"
    assert cutover["successor_branches_created"] is False
