from pathlib import Path


def test_task7_checkpoint_does_not_claim_green_or_live_effects() -> None:
    text = Path("docs/checkpoints/RADAR_TASK7_SOURCE_STATE_2026-09-06.md").read_text(encoding="utf-8")
    assert "source state only" in text
    assert "No Supabase migration was applied" in text
    assert "Full repository GitHub Actions verification remains required" in text
