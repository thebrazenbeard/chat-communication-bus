import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CUTOVER_MAIN_SHA = "b332ca4969b11ac0af3436a33f3c42908356fb88"
TOPOLOGY_SWITCH_MERGE_SHA = "0dc9f821be363c2862309c166ec2eb43b4879b37"
TOPOLOGY_SWITCH_MERGED_AT = "2026-09-04T11:37:28Z"


def _topology():
    return json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json").read_text(encoding="utf-8")
    )


def _cutover():
    return json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_WRITER_LANE_V2_CUTOVER.json").read_text(encoding="utf-8")
    )


def _non_active_topology_identities(topology):
    return {
        identity
        for identity, record in topology["required_writer_lanes"].items()
        if record.get("lifecycle", "ACTIVE") != "ACTIVE"
    }


def test_effective_topology_routes_verified_successors_except_brigit_legacy_exception():
    lanes = _topology()["required_writer_lanes"]
    assert lanes["radar"]["branch"] == "bus/radar-v2"
    assert lanes["brigit"]["branch"] == "bus/bridget-v1"
    assert lanes["one"]["branch"] == "bus/one-v2"
    assert lanes["hephaestus"]["branch"] == "bus/hephaestus-v3"
    assert lanes["vera"]["branch"] == "bus/vera-v2"


def test_cutover_contract_records_effective_switch_and_historical_snapshots():
    topology = _topology()
    cutover = _cutover()
    assert cutover["status"] == "TOPOLOGY_SWITCH_EFFECTIVE_WITH_BRIGIT_LEGACY_EXCEPTION"
    assert cutover["cutover_main_sha"] == CUTOVER_MAIN_SHA
    assert cutover["topology_switch_merge_sha"] == TOPOLOGY_SWITCH_MERGE_SHA
    assert cutover["topology_switch_merged_at"] == TOPOLOGY_SWITCH_MERGED_AT
    assert cutover["successor_branches_created"] is True
    assert cutover["topology_switched"] is True
    non_active = _non_active_topology_identities(topology)
    cutover_identities = set(topology["required_writer_lanes"]) - non_active
    assert set(cutover["historical_writer_lanes"]) == cutover_identities
    assert set(cutover["verified_successor_heads"]) == cutover_identities
    assert set(cutover["historical_writer_lanes"]) == set(cutover["planned_current_writer_lanes"])
    assert cutover["current_writer_lanes"] == {
        identity: record["branch"]
        for identity, record in topology["required_writer_lanes"].items()
        if identity not in non_active
    }
    for identity, head in cutover["verified_successor_heads"].items():
        assert head == CUTOVER_MAIN_SHA, identity
    for identity, predecessor in cutover["historical_writer_lanes"].items():
        assert predecessor["head_sha"] is not None, identity
    assert cutover["blocked_identities"] == {}
    assert cutover["protected_effects"] == {
        "topology_switch_merge_observed": True,
        "provider_cutover": False,
        "ruleset_change": False,
    }


def test_brigit_legacy_exception_records_resolved_duplicate_without_activation():
    topology = _topology()
    cutover = _cutover()
    exception = cutover["legacy_exceptions"]["brigit"]
    historical_block = cutover["historical_blocks"]["brigit"]

    assert topology["required_writer_lanes"]["brigit"]["branch"] == "bus/bridget-v1"
    assert cutover["current_writer_lanes"]["brigit"] == "bus/bridget-v1"
    assert cutover["planned_current_writer_lanes"]["brigit"] == "bus/brigit-v2"
    assert exception["current_branch"] == "bus/bridget-v1"
    assert exception["planned_successor_branch"] == "bus/brigit-v2"
    assert exception["correction_message_id"] == "brigit-0025"
    assert exception["correction_commit"] == "de65639382b310819bc649abf3d12c42d0f23194"
    assert exception["correction_readback_blob"] == "7f26cbd019238bb4a95b67220e0005c4b8b028b9"
    assert exception["correction_ack_message_id"] == "brigit-0026"
    assert exception["correction_ack_commit"] == "ac02fe3e77c0db3da90b1a4105fe69dc30a8e76d"
    assert exception["successor_activation_performed"] is False
    assert historical_block["reason"] == "DUPLICATE_NEW_MESSAGE_ID"
    assert historical_block["failed_projection_run_id"] == 33866555843
    assert historical_block["correction_requested_message_id"] == "radar-0039"
    assert historical_block["resolved"] is True


def test_cutover_contract_records_latest_radar_predecessor_message_in_final_snapshot():
    cutover = _cutover()
    assert cutover["historical_writer_lanes"]["radar"]["head_sha"] == "b25416b3f16d20d1fc1cbe862bf8b0f7d719f724"


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
