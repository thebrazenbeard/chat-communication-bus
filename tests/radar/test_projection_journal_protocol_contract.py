from pathlib import Path


def test_projection_journal_protocol_records_source_only_authority_boundary() -> None:
    text = Path("docs/protocol/RADAR_PROJECTION_JOURNAL_V1.md").read_text(encoding="utf-8")
    assert "claiming work cannot create or invent a cursor" in text
    assert "one provider transaction" in text
    assert "has no direct table-write grant" in text
    assert "NOOP" in text and "FORWARD" in text and "STALE_EVENT" in text and "DIVERGED_HISTORY" in text
    assert "Provider deployment, migration application, workflow activation" in text
