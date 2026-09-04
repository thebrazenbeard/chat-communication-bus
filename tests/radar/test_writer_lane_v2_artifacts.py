import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CUTOVER_MAIN_SHA = "b332ca4969b11ac0af3436a33f3c42908356fb88"


def _topology():
    return json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json").read_text(encoding="utf-8")
    )


def _cutover():
    return json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_WRITER_LANE_V2_CUTOVER.json").read_text(encoding="utf-8")
    )


def test_topology_switch_proposal_routes_verified_successors_except_blocked_brigit():
    lanes = _topology()["required_writer_lanes"]
    assert lanes["radar"]["branch"] == "bus/radar-v2"
    assert lanes["brigit"]["branch"] == "bus/bridget-v1"
    assert lanes["one"]["branch"] == "bus/one-v2"
    assert lanes["hephaestus"]["branch"] == "bus/hephaestus-v3"
    assert lanes["vera"]["branch"] == "bus/vera-v2"


def test_cutover_contract_records_verified_successor_fleet_and_predecessor_heads():
    topology = _topology()
    cutover = _cutover()
    assert cutover["status"] == "PARTIAL_TOPOLOGY_SWITCH_PROPOSED"
    assert cutover["cutover_main_sha"] == CUTOVER_MAIN_SHA
    assert cutover["successor_branches_created"] is True
    assert cutover["topology_switched"] is False
    assert set(cutover["historical_writer_lanes"]) == set(topology["required_writer_lanes"])
    assert set(cutover["verified_successor_heads"]) == set(topology["required_writer_lanes"])
    assert set(cutover["historical_writer_lanes"]) == set(cutover["planned_current_writer_lanes"])
    for identity, head in cutover["verified_successor_heads"].items():
        assert head == CUTOVER_MAIN_SHA, identity
    for identity, predecessor in cutover["historical_writer_lanes"].items():
        assert predecessor["head_sha"] is not None, identity
    assert cutover["protected_effects"] == {
        "merge": False,
        "provider_cutover": False,
        "ruleset_change": False,
    }


def test_brigit_block_is_explicit_and_topology_does_not_claim_her_successor_current():
    topology = _topology()
    cutover = _cutover()
    blocked = cutover["blocked_identities"]["brigit"]
    assert topology["required_writer_lanes"]["brigit"]["branch"] == "bus/bridget-v1"
    assert blocked["current_branch"] == "bus/bridget-v1"
    assert blocked["current_head_sha"] == "45b964a2f20ff10818496b87ae30a701070d5dd2"
    assert blocked["reason"] == "DUPLICATE_NEW_MESSAGE_ID"
    assert blocked["failed_projection_run_id"] == 33866555843
    assert blocked["correction_requested_message_id"] == "radar-0039"
    assert cutover["planned_current_writer_lanes"]["brigit"] == "bus/brigit-v2"


def test_cutover_contract_records_latest_radar_predecessor_message_in_final_snapshot():
    cutover = _cutover()
    assert cutover["historical_writer_lanes"]["radar"]["head_sha"] == "bebe04ea25a4a6f4ee7fb89033cdc1355bd2ac91"


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
