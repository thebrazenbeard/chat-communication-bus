from pathlib import Path


def test_task7_required_source_files_exist() -> None:
    for path in (
        "src/radar/reconciliation_journal.py",
        "src/radar/trusted_reconciler.py",
        "supabase/migrations/20260906154101_radar_projection_journal_v1.sql",
        "supabase/tests/radar_projection_journal_v1.sql",
        "docs/protocol/RADAR_PROJECTION_JOURNAL_V1.md",
    ):
        assert Path(path).exists()
