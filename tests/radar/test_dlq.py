import importlib
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
    item_id = store.record(message_id="m1", failure_stage="routing", failure_code="NO_ROUTE", envelope={"message_id": "m1"}, diagnostic="no recipients")
    store.close()
    reopened = m.DeadLetterStore(path)
    item = reopened.inspect(item_id)
    assert item.failure_code == "NO_ROUTE"
    assert item.replay_state == "PENDING"


def test_replay_requires_applicability_refresh(tmp_path):
    m = _module()
    store = m.DeadLetterStore(tmp_path / "dlq.sqlite")
    item_id = store.record(message_id="m2", failure_stage="delivery", failure_code="OFFLINE", envelope={"message_id": "m2"}, diagnostic="target offline")
    with pytest.raises(m.DeadLetterError, match="APPLICABILITY_NOT_REFRESHED"):
        store.mark_replay(item_id)
    store.set_applicability(item_id, "APPLICABLE")
    store.mark_replay(item_id)
    assert store.inspect(item_id).replay_state == "REPLAYED"
