import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CUT = "87df9b1372d0f65b5c3ced0296122b2140084024"


def _topology():
    return json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json").read_text(encoding="utf-8")
    )


def _onboarding():
    return json.loads(
        (
            ROOT
            / "architecture"
            / "contracts"
            / "RADAR_WRITER_LANE_ONBOARDING_ORGASM_VERA_V1.json"
        ).read_text(encoding="utf-8")
    )


def test_orgasm_vera_is_registered_to_exact_inert_lane():
    lane = _topology()["required_writer_lanes"]["orgasm-vera"]
    assert lane == {
        "writer": "Orgasm Vera",
        "branch": "bus/orgasm-vera-v2",
        "legacy_spelling": False,
        "lifecycle": "REGISTERED_INERT",
        "onboarding_status": "FIRST_APPEND_PENDING",
    }
    onboarding = _onboarding()
    assert onboarding["identity"] == "orgasm-vera"
    assert onboarding["writer"] == "Orgasm Vera"
    assert onboarding["branch"] == "bus/orgasm-vera-v2"
    assert onboarding["bootstrap_main_sha"] == CUT
    assert onboarding["bootstrap_branch_head_sha"] == CUT
    assert onboarding["inert_branch_created"] is True
    assert onboarding["topology_pr_merged"] is False


def test_orgasm_vera_coordination_remains_gated_until_registration_and_guard():
    onboarding = _onboarding()
    assert onboarding["lifecycle"] == "REGISTERED_INERT"
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


def test_orgasm_vera_onboarding_preserves_private_zero_cost_role_split():
    onboarding = _onboarding()
    effects = onboarding["protected_effects"]
    assert effects == {
        "topology_merge": False,
        "first_append_write": False,
        "provider_projection": False,
        "ruleset_change": False,
        "paid_infrastructure": False,
    }
    role = onboarding["role_scope"]
    assert role["project_lead"] == "Orgasm Vera"
    assert role["hostile_reviewer"] == "Vera"
    assert role["cohesion_collaborator"] == "Cohesion Vera"
    assert role["independent_validator"] == "Thirteen"
    assert role["cost_boundary"] == "ZERO_COST_UNLESS_PATRICK_EXPLICITLY_AUTHORIZES_PAID_EFFECT"
    notes = "\n".join(onboarding["notes"])
    assert "private" in notes.lower()
    assert "zero-cost" in notes.lower()
