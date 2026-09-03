import importlib
from pathlib import Path

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


def test_singular_hub_policy_preserves_patrick_directive_without_invented_contract():
    policy = Path("docs/protocol/COMMUNICATION_HUB_V1.md").read_text(encoding="utf-8")
    bootstrap = Path("docs/protocol/EXTERNAL_PR_MIRROR_BOOTSTRAP_2026-09-03.md").read_text(encoding="utf-8")

    assert "All messages/communications that are not pull requests" in policy
    assert "Any pull requests in projects/repos done outside" in policy

    for invented_requirement in (
        "mirror_type: PR_MIRROR",
        "The initial PR mirror MUST record at least",
        "Material PR lifecycle events MUST be mirrored",
        "default mirror location",
    ):
        assert invented_requirement not in policy

    assert "historical, non-normative snapshot" in bootstrap
    assert "must be recorded as append-only Bus messages" not in bootstrap


def test_thread_closure_contract_is_exact_prospective_and_separate_from_assignments():
    protocol = Path("docs/protocol/PROTOCOL_V2.md").read_text(encoding="utf-8")
    closure = Path("docs/protocol/THREAD_CLOSURE_V1.md").read_text(encoding="utf-8")

    assert "THREAD_CLOSURE_V1.md" in protocol
    assert "addressed + read" in closure.lower()
    assert "same active turn" in closure.lower()
    assert "#ENDTHREAD" in closure
    assert "exact standalone final non-whitespace line" in closure
    assert "case-sensitive" in closure
    assert "requires_reply: false" in closure
    assert "does not remove" in closure.lower() and "reply obligation" in closure.lower()
    assert "prospective" in closure.lower()
    assert "historical" in closure.lower()
    assert "assignment lifecycle" in closure.lower()
    assert "does not cancel" in closure.lower()
    assert "unread" in closure.lower()
    assert "does not prove" in closure.lower()
