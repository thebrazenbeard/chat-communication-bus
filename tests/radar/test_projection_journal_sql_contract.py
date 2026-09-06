from pathlib import Path


MIGRATION = Path(
    "supabase/migrations/20260906154101_radar_projection_journal_v1.sql"
)
OLD_MIGRATION = Path(
    "supabase/migrations/20260906154500_radar_projection_journal_v1.sql"
)
SQL_TEST = Path("supabase/tests/radar_projection_journal_v1.sql")


def test_projection_journal_migration_is_uniquely_versioned_and_fenced() -> None:
    assert MIGRATION.exists()
    assert not OLD_MIGRATION.exists()
    source = MIGRATION.read_text(encoding="utf-8")

    for table in (
        "radar.projection_lane_state",
        "radar.projection_batches",
        "radar.projection_batch_files",
    ):
        assert f"revoke all on table {table} from public, anon, authenticated, service_role;" in source

    for function in (
        "radar.projection_seed_lane_v1",
        "radar.projection_set_control_cut_v1",
        "radar.projection_claim_batch_v1",
        "radar.projection_record_file_result_v1",
        "radar.projection_finalize_batch_v1",
    ):
        assert f"create or replace function {function}" in source

    assert source.count("security definer") >= 5
    assert "RADAR_PROJECTION_LANE_UNSEEDED" in source
    assert "RADAR_PROJECTION_CONTROL_CUT_CHANGED" in source
    assert "RADAR_PROJECTION_BASE_CHANGED" in source
    assert "RADAR_PROJECTION_UNRESOLVED_FILES" in source
    assert "grant select, insert" not in source
    assert "grant update" not in source


def test_projection_journal_has_rollback_sql_assertions() -> None:
    assert SQL_TEST.exists()
    test_sql = SQL_TEST.read_text(encoding="utf-8")
    assert test_sql.lstrip().startswith("-- Run after applying")
    assert "RADAR_TEST_EXPECTED_LANE_UNSEEDED" in test_sql
    assert "RADAR_TEST_EXPECTED_STALE_CLAIM" in test_sql
    assert "RADAR_TEST_EXPECTED_CONTROL_CUT_CHANGED" in test_sql
    assert "RADAR_PROJECTION_DIRECT_WRITE_EXPOSED" in test_sql
    assert test_sql.rstrip().endswith("rollback;")
