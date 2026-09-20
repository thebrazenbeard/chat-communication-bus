import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "architecture/contracts/ASSIGNMENT_EXECUTION_CLAIM_V1.json"
ADR = ROOT / "architecture/decisions/ADR-0005-assignment-runtime-instance-fencing.md"
MIGRATIONS = ROOT / "supabase/migrations"


def load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_fencing_design_separates_durable_identity_from_runtime():
    d = load()
    assert d["status"] == "DESIGN_ONLY_NOT_INSTALLED"
    assert d["identity_model"]["durable_worker_identity_field"] == "assignee_identity_id"
    assert d["identity_model"]["runtime_instance_field"] == "node_id"
    assert d["identity_model"]["durable_identity_is_not_runtime_identity"] is True
    assert d["identity_model"]["execution_claim_is_not_authority"] is True


def test_fencing_design_binds_assignment_event_node_and_monotonic_token():
    d = load()
    fields = set(d["current_claim"]["fields"])
    assert {"assignment_id", "assignee_identity_id", "node_id", "fence_token",
            "bound_assignment_event_id", "lease_expires_at", "last_operation_id"} <= fields
    assert d["fence"]["takeover_requires_strictly_newer_token"] is True
    assert d["fence"]["old_token_after_takeover_rejected"] is True
    assert d["renew"]["requires_same_bound_assignment_event"] is True


def test_fencing_design_is_lease_and_dependency_bounded():
    d = load()
    assert d["acquire"]["requires_node_live"] is True
    assert d["acquire"]["requires_node_lease_unexpired"] is True
    assert d["acquire"]["claim_lease_must_not_exceed_node_lease"] is True
    assert d["renew"]["claim_lease_must_not_exceed_node_lease"] is True
    assert d["acquire"]["requires_dependency_readiness"] is True


def test_fencing_design_requires_idempotency_and_stale_rejection():
    d = load()
    assert d["acquire"]["same_operation_id_is_idempotent"] is True
    assert d["renew"]["same_operation_id_is_idempotent"] is True
    assert d["release_or_finalize"]["lost_response_retry_must_not_create_new_generation"] is True
    assert d["assignment_successor_binding"]["stale_node_or_token_rejected"] is True
    assert d["assignment_successor_binding"]["superseded_assignment_event_rejected"] is True


def test_fencing_design_preserves_protected_effect_separation():
    d = load()
    authority = d["authority_separation"]
    assert all(authority.values())
    security = d["security"]
    assert security["claim_mutation_functions_service_role_only"] is True
    assert security["anon_execute_forbidden"] is True
    assert security["authenticated_execute_forbidden"] is True


def test_fencing_design_freezes_issue_142_hostile_matrix():
    d = load()
    cases = set(d["required_hostile_cases"])
    required = {
        "two_live_nodes_race_for_one_assignment",
        "loser_continues_from_stale_local_state",
        "winner_lease_expires_successor_takes_over",
        "old_worker_attempts_completion_after_takeover",
        "assignment_advances_while_claim_held",
        "protected_effect_authority_remains_separate",
        "lost_response_retry_does_not_duplicate_execution",
        "claim_lease_cannot_exceed_node_lease",
        "node_identity_mismatch_cannot_claim",
        "old_fence_token_replay_after_takeover_rejected",
        "same_operation_id_is_idempotent",
        "control_plane_advance_invalidates_stale_execution_ownership",
        "claim_acquisition_cannot_bypass_dependency_readiness",
        "claim_mutation_not_executable_by_anon_or_authenticated",
    }
    assert required <= cases


def test_design_branch_does_not_install_runtime_fencing():
    d = load()
    assert d["security"]["source_design_does_not_authorize_provider_application"] is True
    assert not any("assignment_execution" in p.name and "fenc" in p.name for p in MIGRATIONS.glob("*.sql"))
    text = ADR.read_text(encoding="utf-8").lower()
    assert "design only" in text
    assert "does not authorize application" in text
