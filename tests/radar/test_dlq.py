import importlib
import sqlite3

import pytest


def _module():
    try:
        return importlib.import_module("radar.dlq")
    except Exception as exc:
        pytest.fail(f"Radar DLQ implementation missing: {exc}")


def test_dead_letter_survives_store_reopen(tmp_path):
    m = _module()
    path = tmp_path / "radar-dlq.sqlite"
    store = m.DeadLetterStore(path)
    item_id = store.record(
        message_id="m1",
        failure_stage="routing",
        failure_code="NO_ROUTE",
        envelope={"message_id": "m1"},
        diagnostic="no recipients",
    )
    store.close()
    reopened = m.DeadLetterStore(path)
    item = reopened.inspect(item_id)
    assert item.failure_code == "NO_ROUTE"
    assert item.replay_state == "PENDING"


def test_replay_requires_applicability_refresh(tmp_path):
    m = _module()
    store = m.DeadLetterStore(tmp_path / "dlq.sqlite")
    item_id = store.record(
        message_id="m2",
        failure_stage="delivery",
        failure_code="OFFLINE",
        envelope={"message_id": "m2"},
        diagnostic="target offline",
    )
    with pytest.raises(m.DeadLetterError, match="APPLICABILITY_NOT_REFRESHED"):
        store.mark_replay(item_id)
    store.set_applicability(item_id, "APPLICABLE")
    store.mark_replay(item_id)
    assert store.inspect(item_id).replay_state == "REPLAYED"


def test_dead_letter_preserves_source_locator_and_reason_category(tmp_path):
    m = _module()
    path = tmp_path / "evidence.sqlite"
    store = m.DeadLetterStore(path)
    item_id = store.record(
        message_id="m3",
        failure_stage="admission",
        failure_code="UNKNOWN_DOMAIN",
        envelope={"message_id": "m3", "domain": "bogus"},
        diagnostic="domain not registered",
        reason_category="TAXONOMY",
        source_locator="git:bus/one-v2@abc123:messages/one-0003.md",
    )
    store.close()

    reopened = m.DeadLetterStore(path)
    item = reopened.inspect(item_id)
    assert item.reason_category == "TAXONOMY"
    assert item.source_locator == "git:bus/one-v2@abc123:messages/one-0003.md"


def test_existing_dlq_database_is_migrated_additively(tmp_path):
    m = _module()
    path = tmp_path / "legacy.sqlite"
    connection = sqlite3.connect(path)
    connection.execute(
        """
        CREATE TABLE radar_dead_letters (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT NOT NULL,
            failure_stage TEXT NOT NULL,
            failure_code TEXT NOT NULL,
            envelope_json TEXT NOT NULL,
            diagnostic TEXT NOT NULL,
            applicability TEXT NOT NULL DEFAULT 'UNKNOWN',
            replay_state TEXT NOT NULL DEFAULT 'PENDING',
            retry_count INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    connection.execute(
        """
        INSERT INTO radar_dead_letters
            (message_id, failure_stage, failure_code, envelope_json, diagnostic)
        VALUES ('legacy-1', 'routing', 'NO_ROUTE', '{"message_id":"legacy-1"}', 'legacy')
        """
    )
    connection.commit()
    connection.close()

    store = m.DeadLetterStore(path)
    item = store.inspect(1)
    assert item.reason_category == "UNCLASSIFIED"
    assert item.source_locator is None
