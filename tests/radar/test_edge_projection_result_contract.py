from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HANDLER = ROOT / "supabase/functions/github-bus-ingest/handler.ts"
COLLISION_SQL = ROOT / "supabase/migrations/20260902231445_radar_live_message_collision_v1.sql"


def test_edge_projection_result_mapping_is_explicit_and_fail_closed() -> None:
    source = HANDLER.read_text(encoding="utf-8")

    assert "function projectionResultState" in source
    assert 'result === "INSERTED"' in source
    assert 'result.startsWith("CONFLICT_INSERTED:")' in source
    assert 'result === "IDEMPOTENT"' in source
    assert 'result.startsWith("CONFLICT_IDEMPOTENT:")' in source
    assert 'throw new HttpError(502, "PROJECTION_RPC_RESULT_INVALID")' in source
    assert "const state = projectionResultState(result);" in source
    assert 'result === "CONFLICT"' not in source


def test_edge_projection_result_mapping_covers_every_sql_terminal_outcome() -> None:
    sql = COLLISION_SQL.read_text(encoding="utf-8")

    for result in (
        "INSERTED",
        "IDEMPOTENT",
        "CONFLICT_INSERTED:",
        "CONFLICT_IDEMPOTENT:",
    ):
        assert result in sql
