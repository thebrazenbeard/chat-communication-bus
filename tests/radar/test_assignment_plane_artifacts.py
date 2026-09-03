from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "supabase" / "migrations" / "20260903_radar_assignment_plane_v1.sql"
CONTRACT = ROOT / "docs" / "protocol" / "ASSIGNMENT_ENVELOPE_V1.md"


def test_assignment_plane_requires_explicit_structured_envelope():
    sql = MIGRATION.read_text().lower()
    assert "assignment_id" in sql
    assert "assignment_workflow_id" in sql
    assert "assignment_assignee" in sql
    assert "assignment_event" in sql
    assert "assignment_state" in sql
    assert "assignment_predecessor_message_id" in sql
    assert "create or replace function radar.reconcile_bus_assignments_v1" in sql


def test_assignment_plane_adds_owner_and_source_receipts():
    sql = MIGRATION.read_text().lower()
    assert "add column if not exists assignee_identity_id" in sql
    assert "add column if not exists source_message_id" in sql
    assert "references radar.identities" in sql
    assert "references radar.messages" in sql


def test_assignment_plane_fails_closed_on_missing_predecessor_or_fork():
    sql = MIGRATION.read_text()
    assert "ASSIGNMENT_EVENT_PENDING_PREDECESSOR" in sql
    assert "ASSIGNMENT_EVENT_CONFLICT" in sql
    assert "ASSIGNMENT_ENVELOPE_INVALID" in sql
    assert "current_event_id" in sql
    assert "predecessor_event_id" in sql


def test_assignment_plane_is_idempotent_and_not_nlp_inference():
    sql = MIGRATION.read_text().lower()
    assert "on conflict (assignment_id, operation_id) do nothing" in sql
    assert "payload->>'assignment_id'" in sql
    assert "payload->>'assignment_event'" in sql
    assert "delete from radar.assignments" not in sql
    assert "delete from radar.assignment_events" not in sql
    contract = CONTRACT.read_text().lower()
    assert "no natural-language inference" in contract
    assert "assignment_assignee" in contract
    assert "assignment_predecessor_message_id" in contract
