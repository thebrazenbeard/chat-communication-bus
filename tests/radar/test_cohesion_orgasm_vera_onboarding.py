import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CUT = "87df9b1372d0f65b5c3ced0296122b2140084024"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_specialized_vera_lanes_are_registered_inert_from_same_cut():
    topology = load("architecture/contracts/RADAR_TOPOLOGY_V1.json")
    expected = {
        "cohesion-vera": ("Cohesion Vera", "bus/cohesion-vera-v2"),
        "orgasm-vera": ("Orgasm Vera", "bus/orgasm-vera-v2"),
    }
    for identity, (writer, branch) in expected.items():
        lane = topology["required_writer_lanes"][identity]
        assert lane == {
            "writer": writer,
            "branch": branch,
            "legacy_spelling": False,
            "lifecycle": "REGISTERED_INERT",
            "onboarding_status": "FIRST_APPEND_PENDING",
        }


def test_each_specialized_lane_requires_its_own_guarded_first_append():
    files = {
        "cohesion-vera": "architecture/contracts/RADAR_WRITER_LANE_ONBOARDING_COHESION_VERA_V1.json",
        "orgasm-vera": "architecture/contracts/RADAR_WRITER_LANE_ONBOARDING_ORGASM_VERA_V1.json",
    }
    for identity, path in files.items():
        onboarding = load(path)
        assert onboarding["identity"] == identity
        assert onboarding["bootstrap_main_sha"] == CUT
        assert onboarding["bootstrap_branch_head_sha"] == CUT
        assert onboarding["lifecycle"] == "REGISTERED_INERT"
        assert onboarding["inert_branch_created"] is True
        assert onboarding["topology_pr_merged"] is False
        assert onboarding["first_append_guard_verified"] is False
        assert onboarding["sequence"] == [
            "CREATE_INERT_BRANCH_FROM_EXACT_MAIN",
            "VERIFY_INERT_BRANCH_HEAD",
            "MERGE_TOPOLOGY_REGISTRATION",
            "APPEND_ONE_MESSAGE",
            "VERIFY_CURRENT_WRITER_LANE_GUARD",
            "ENABLE_WORKER_COORDINATION",
        ]
        gate = onboarding["coordination_gate"]
        assert "first_append_guard_verified" in gate
        assert "lifecycle is ACTIVE" in gate


def test_private_zero_cost_role_split_is_preserved():
    cohesion = load("architecture/contracts/RADAR_WRITER_LANE_ONBOARDING_COHESION_VERA_V1.json")
    orgasm = load("architecture/contracts/RADAR_WRITER_LANE_ONBOARDING_ORGASM_VERA_V1.json")

    for onboarding in (cohesion, orgasm):
        assert onboarding["protected_effects"] == {
            "topology_merge": False,
            "first_append_write": False,
            "provider_projection": False,
            "ruleset_change": False,
            "paid_infrastructure": False,
        }
        notes = "\n".join(onboarding["notes"]).lower()
        assert "private" in notes
        assert "zero-cost" in notes

    assert cohesion["role_scope"]["project_lead"] == "Cohesion Vera"
    assert cohesion["role_scope"]["hostile_reviewer"] == "Vera"
    assert cohesion["role_scope"]["orgasm_collaborator"] == "Orgasm Vera"
    assert cohesion["role_scope"]["independent_validator"] == "Thirteen"

    assert orgasm["role_scope"]["project_lead"] == "Orgasm Vera"
    assert orgasm["role_scope"]["hostile_reviewer"] == "Vera"
    assert orgasm["role_scope"]["cohesion_collaborator"] == "Cohesion Vera"
    assert orgasm["role_scope"]["independent_validator"] == "Thirteen"
