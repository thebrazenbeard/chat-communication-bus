from pathlib import Path


def test_task7_does_not_activate_live_workflows_or_provider_effects() -> None:
    migration = Path("supabase/migrations/20260906154101_radar_projection_journal_v1.sql").read_text(encoding="utf-8")
    protocol = Path("docs/protocol/RADAR_PROJECTION_JOURNAL_V1.md").read_text(encoding="utf-8")
    assert "Source-only until separately authorized provider migration." in migration
    assert "Provider deployment, migration application, workflow activation" in protocol
