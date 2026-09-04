from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "supabase" / "migrations" / "20260903_radar_operator_views_v1.sql"
THREAD_CLOSURE_MIGRATION = ROOT / "supabase" / "migrations" / "20260903_radar_thread_closure_v1.sql"
CONTRACT = ROOT / "docs" / "protocol" / "OPERATOR_VIEWS_V1.md"
THREAD_CLOSURE_CONTRACT = ROOT / "docs" / "protocol" / "THREAD_CLOSURE_V1.md"


def test_operator_views_separate_reply_evidence_from_read_state():
    sql = MIGRATION.read_text().lower()
    assert "create or replace view radar.identity_message_status_v1" in sql
    assert "indexed_not_delivered" in sql
    assert "explicit_reply_evidence" in sql
    assert "no_explicit_reply_evidence" in sql
    assert "unread" not in sql


def test_operator_views_expose_open_assignments_without_guessing_from_messages():
    sql = MIGRATION.read_text().lower()
    marker = "create or replace view radar.open_assignments_v1"
    assert marker in sql
    assignment_sql = sql.split(marker, 1)[1]
    assert "from radar.assignments" in assignment_sql
    assert "assignee_identity_id" in assignment_sql
    assert "current_state not in ('confirmed','stopped','superseded')" in assignment_sql
    assert "payload->>'subject'" not in assignment_sql


def test_operator_views_include_exact_receipt_and_current_event_evidence():
    sql = MIGRATION.read_text().lower()
    assert "source_message_id" in sql
    assert "current_event_id" in sql
    assert "operation_id" in sql
    assert "receipt_sha256" in sql
    assert "evidence_ref" in sql


def test_thread_closure_view_keeps_reply_and_closure_evidence_distinct():
    sql = THREAD_CLOSURE_MIGRATION.read_text().lower()
    assert "create or replace view radar.identity_message_status_v2" in sql
    assert "conversation_closed_by_sender" in sql
    assert "reply_evidence_present" in sql
    assert "closed_by_endthread" in sql
    assert "no_reply_evidence_yet" in sql
    assert "indexed_not_delivered" in sql
    assert "unread" not in sql
    assert "ignored" not in sql
    assert "radar.open_assignments_v1" not in sql


def test_thread_closure_view_never_projects_historical_reply_obligation_claims():
    sql = THREAD_CLOSURE_MIGRATION.read_text().lower()
    contract = THREAD_CLOSURE_CONTRACT.read_text().lower()
    for forbidden_obligation_claim in ("reply_owed", "reply_obligation", "overdue_reply", "ignored_by_recipient"):
        assert forbidden_obligation_claim not in sql
    assert "prospective" in contract
    assert "historical messages" in contract
    assert "do not become newly owed replies" in contract
    assert "no_reply_evidence_yet" in sql


def test_operator_contract_preserves_claim_ceiling():
    text = CONTRACT.read_text().lower()
    assert "no_explicit_reply_evidence" in text
    assert "does not mean unread" in text
    assert "open assignment" in text
    assert "git remains canonical" in text
