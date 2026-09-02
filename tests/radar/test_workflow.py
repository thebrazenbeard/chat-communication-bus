import importlib
import pytest


def _module():
    try:
        return importlib.import_module("radar.workflow")
    except Exception as exc:
        pytest.fail(f"Radar workflow implementation missing: {exc}")


def test_missing_required_lane_is_action_not_blocker():
    m = _module()
    finding = m.classify_lane_requirement(required=True, exists=False)
    assert finding == "ACTION_REQUIRED:CREATE_LANE"


def test_isolated_branch_authority_does_not_imply_merge_authority():
    m = _module()
    scope = m.EffectScope(isolated_branch=True, merge=False, deploy=False)
    assert scope.allows("create_branch") is True
    assert scope.allows("write_isolated") is True
    assert scope.allows("merge") is False


def test_dependency_completion_makes_successor_ready_without_protected_authority():
    m = _module()
    g = m.DependencyGraph()
    g.add_assignment("yang-005")
    g.add_assignment("yin-005")
    g.add_edge("yang-005", "yin-005")
    assert g.ready("yin-005") is False
    g.complete("yang-005")
    assert g.ready("yin-005") is True
    assert g.protected_authority("yin-005") is False


def test_cycle_is_rejected():
    m = _module()
    g = m.DependencyGraph()
    g.add_assignment("a")
    g.add_assignment("b")
    g.add_edge("a", "b")
    with pytest.raises(m.WorkflowError, match="DEPENDENCY_CYCLE"):
        g.add_edge("b", "a")
