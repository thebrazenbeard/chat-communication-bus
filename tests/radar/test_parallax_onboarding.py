import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CUT = "b2950bcb547fb78d16e44cd94a6ba2164937bf44"


def _topology():
    return json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json").read_text(encoding="utf-8")
    )


def _onboarding():
    return json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_WRITER_LANE_ONBOARDING_V1.json").read_text(encoding="utf-8")
    )


def test_parallax_is_registered_to_exact_inert_lane():
    lane = _topology()["required_writer_lanes"]["parallax"]
    assert lane == {"writer": "Parallax", "branch": "bus/parallax-v1", "legacy_spelling": False, "onboarding_status": "TOPOLOGY_PR_PENDING"}
    onboarding = _onboarding()
    assert onboarding["identity"] == "parallax"
    assert onboarding["branch"] == "bus/parallax-v1"
    assert onboarding["bootstrap_main_sha"] == CUT
    assert onboarding["bootstrap_branch_head_sha"] == CUT
    assert onboarding["inert_branch_created"] is True
    assert onboarding["topology_pr_merged"] is False


def test_parallax_coordination_requires_first_guarded_append():
    onboarding = _onboarding()
    assert onboarding["sequence"] == [
        "CREATE_INERT_BRANCH_FROM_EXACT_MAIN",
        "VERIFY_INERT_BRANCH_HEAD",
        "MERGE_TOPOLOGY_REGISTRATION",
        "APPEND_ONE_MESSAGE",
        "VERIFY_CURRENT_WRITER_LANE_GUARD",
        "ENABLE_WORKER_COORDINATION",
    ]
    assert onboarding["first_append_guard_verified"] is False
    assert "first_append_guard_verified" in onboarding["coordination_gate"]


def test_parallax_bootstrap_does_not_authorize_provider_or_protected_effects():
    effects = _onboarding()["protected_effects"]
    assert effects == {
        "topology_merge": False,
        "first_append_write": False,
        "provider_projection": False,
        "ruleset_change": False,
    }
