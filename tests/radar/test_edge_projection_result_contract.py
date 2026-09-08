from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HANDLER = ROOT / "supabase/functions/github-bus-ingest/handler.ts"
COLLISION_SQL = ROOT / "supabase/migrations/20260902231445_radar_live_message_collision_v1.sql"
ATOMIC_SQL = ROOT / "supabase/migrations/20260908010500_radar_projection_atomic_file_v1.sql"


def test_edge_projection_result_mapping_is_explicit_and_fail_closed() -> None:
    source = HANDLER.read_text(encoding="utf-8")

    assert "function projectionResultState" in source
    assert 'result === "INSERTED"' in source
    assert 'result.startsWith("CONFLICT_INSERTED:")' in source
    assert 'result === "IDEMPOTENT"' in source
    assert 'result.startsWith("CONFLICT_IDEMPOTENT:")' in source
    assert 'throw new HttpError(502, "PROJECTION_RPC_RESULT_INVALID")' in source
    assert "projectionResultState(result);" in source
    assert 'result === "CONFLICT"' not in source


def test_edge_uses_atomic_claim_validated_file_projection_rpc() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    atomic_sql = ATOMIC_SQL.read_text(encoding="utf-8")

    assert 'supabase.rpc("radar_projection_project_file_v1"' in source
    assert "p_batch_id: batch.batch_id" in source
    assert "p_claim_token: batch.claim_token" in source
    assert "p_path: file.path" in source
    assert 'supabase.rpc("radar_project_bus_message_v1"' not in source
    assert 'supabase.rpc("radar_projection_record_file_result_v1"' not in source
    assert "async function recordFileResult" not in source

    assert "create or replace function radar.projection_project_file_v1" in atomic_sql.lower()
    assert "create or replace function public.radar_projection_project_file_v1" in atomic_sql.lower()
    assert "from service_role" in atomic_sql.lower()
    assert "radar.project_bus_message_v1" in atomic_sql
    assert "radar.projection_record_file_result_v1" in atomic_sql


def test_edge_recipient_header_compatibility_matches_python_grammar() -> None:
    source = HANDLER.read_text(encoding="utf-8")

    assert "function intendedRecipient(headers: Headers): string" in source
    assert 'headers.intended_recipient' in source
    assert 'headers.intended_recipients' in source
    assert '"CONFLICTING_INTENDED_RECIPIENT_HEADERS"' in source
    assert "const intended = intendedRecipient(headers);" in source


def test_edge_projection_result_mapping_covers_every_sql_terminal_outcome() -> None:
    sql = COLLISION_SQL.read_text(encoding="utf-8")

    for result in (
        "INSERTED",
        "IDEMPOTENT",
        "CONFLICT_INSERTED:",
        "CONFLICT_IDEMPOTENT:",
    ):
        assert result in sql
