from pathlib import Path


MIGRATION = Path(
    "supabase/migrations/20260906165117_radar_projection_journal_api_v1.sql"
)


def test_projection_journal_bridge_is_service_only_and_does_not_expose_seed() -> None:
    source = MIGRATION.read_text(encoding="utf-8")
    lowered = source.lower()

    expected = (
        "radar_projection_get_lane_v1",
        "radar_projection_set_control_cut_v1",
        "radar_projection_claim_batch_v1",
        "radar_projection_record_file_result_v1",
        "radar_projection_finalize_batch_v1",
    )
    for name in expected:
        assert f"create or replace function public.{name}" in lowered
        assert f"grant execute on function public.{name}" in lowered
    assert "public.radar_projection_seed" not in lowered
    assert "security definer" in lowered
    assert "set search_path = pg_catalog, radar" in lowered
    assert "from public, anon, authenticated" in lowered
