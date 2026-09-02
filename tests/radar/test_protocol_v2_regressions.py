import importlib
import pytest


def _workflow():
    try:
        return importlib.import_module("radar.workflow")
    except Exception as exc:
        pytest.fail(f"Radar workflow implementation missing: {exc}")


@pytest.mark.parametrize("identity", ["six", "seven", "nine", "masa", "hephaestus"])
def test_assigned_missing_bus_lane_means_create_lane(identity):
    m = _workflow()
    assert m.classify_lane_requirement(required=True, exists=False) == "ACTION_REQUIRED:CREATE_LANE"


def test_specific_branch_instruction_beats_stale_local_only_for_branch_scope():
    m = _workflow()
    effective = m.resolve_effect_scope(
        older={"local_only": True, "merge": False, "deploy": False},
        newer={"create_isolated_branch": True},
    )
    assert effective.allows("create_branch") is True
    assert effective.allows("write_isolated") is True
    assert effective.allows("merge") is False
    assert effective.allows("deploy") is False


def test_reversible_exact_assignment_needs_no_second_permission_token():
    m = _workflow()
    decision = m.execution_decision(action="create_branch", explicitly_assigned=True, reversible=True, protected=False, ambiguous=False)
    assert decision == "DO_VERIFY_REPORT"


def test_protected_or_materially_ambiguous_effect_still_stops():
    m = _workflow()
    assert m.execution_decision(action="merge", explicitly_assigned=True, reversible=False, protected=True, ambiguous=False) == "REQUIRE_EXACT_AUTHORITY"
    assert m.execution_decision(action="unknown_external_write", explicitly_assigned=True, reversible=False, protected=False, ambiguous=True) == "REQUIRE_CLARIFICATION"
