from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "supabase" / "migrations" / "20260903000603_radar_receipt_plane_v1.sql"


def test_receipt_plane_migration_exists_and_separates_indexing_from_delivery():
    sql = MIGRATION.read_text()
    lowered = sql.lower()
    assert "create or replace function radar.reconcile_bus_receipts_v1" in lowered
    assert "projected_for_identity" in lowered
    assert "indexed_not_delivered" in lowered
    assert "acknowledgement_type" in lowered
    assert "'read'" in lowered
    assert "ambiguous_reply_reference" in lowered


def test_receipt_plane_is_idempotent_and_append_only_friendly():
    sql = MIGRATION.read_text()
    lowered = sql.lower()
    assert "on conflict" in lowered
    assert "create unique index if not exists radar_delivery_projected_identity_unique_idx" in lowered
    assert "delete from radar.delivery_events" not in lowered
    assert "delete from radar.acknowledgements" not in lowered
    assert "after insert on radar.messages" in lowered


def test_receipt_plane_fails_closed_on_ambiguous_declared_ids():
    sql = MIGRATION.read_text()
    lowered = sql.lower()
    assert "candidate_count = 1" in lowered
    assert "candidate_count > 1" in lowered
    assert "declared_message_id" in lowered
