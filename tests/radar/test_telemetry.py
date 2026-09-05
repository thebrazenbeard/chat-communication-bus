import inspect

import pytest

from radar.telemetry import HEARTBEAT_INTERVAL_MS, TelemetryStore


def test_counters_and_heartbeat_survive_reopen(tmp_path):
    path = tmp_path / "telemetry.sqlite"
    store = TelemetryStore(path)
    store.increment("routed", 2)
    store.increment("dropped")
    store.increment("dlq", 3)
    first = store.emit_heartbeat(1_000, source_ref="main@abc", provider_state="DEGRADED")
    assert first is not None
    assert first["domain"] == "system"
    assert first["intent"] == "telemetry"
    assert first["counts"] == {"routed": 2, "dropped": 1, "dlq": 3}
    store.close()

    reopened = TelemetryStore(path)
    assert reopened.snapshot().as_dict() == {"routed": 2, "dropped": 1, "dlq": 3}
    assert reopened.emit_heartbeat(1_000 + HEARTBEAT_INTERVAL_MS - 1) is None
    second = reopened.emit_heartbeat(1_000 + HEARTBEAT_INTERVAL_MS)
    assert second is not None
    assert second["counts"] == {"routed": 2, "dropped": 1, "dlq": 3}


def test_heartbeat_includes_last_source_and_provider_evidence(tmp_path):
    store = TelemetryStore(tmp_path / "telemetry.sqlite")
    heartbeat = store.emit_heartbeat(
        42,
        source_ref="bus/one-v2@deadbeef",
        provider_state="NOT_ESTABLISHED",
    )
    assert heartbeat is not None
    assert heartbeat["source_ref"] == "bus/one-v2@deadbeef"
    assert heartbeat["provider_state"] == "NOT_ESTABLISHED"


def test_invalid_counter_and_time_fail_closed(tmp_path):
    store = TelemetryStore(tmp_path / "telemetry.sqlite")
    with pytest.raises(ValueError, match="UNKNOWN_TELEMETRY_COUNTER"):
        store.increment("unknown")
    with pytest.raises(ValueError, match="INVALID_TELEMETRY_INCREMENT"):
        store.increment("routed", True)
    with pytest.raises(ValueError, match="INVALID_HEARTBEAT_TIME"):
        store.emit_heartbeat(-1)
    with pytest.raises(ValueError, match="INVALID_HEARTBEAT_TIME"):
        store.emit_heartbeat(True)


def test_thread_sharing_is_explicit_opt_in():
    default = inspect.signature(TelemetryStore).parameters["check_same_thread"].default
    assert default is True


def test_wal_mode_does_not_weaken_durable_synchronous_setting(tmp_path):
    store = TelemetryStore(tmp_path / "telemetry.sqlite")
    synchronous = int(store.connection.execute("PRAGMA synchronous").fetchone()[0])
    assert synchronous == 2  # SQLite FULL


def test_clock_regression_fails_closed_instead_of_suppressing_indefinitely(tmp_path):
    store = TelemetryStore(tmp_path / "telemetry.sqlite")
    assert store.emit_heartbeat(100_000) is not None
    with pytest.raises(ValueError, match="HEARTBEAT_CLOCK_REGRESSION"):
        store.emit_heartbeat(99_999)


def test_recent_heartbeats_are_newest_first_and_limit_is_validated(tmp_path):
    store = TelemetryStore(tmp_path / "telemetry.sqlite")
    assert store.emit_heartbeat(1_000) is not None
    assert store.emit_heartbeat(1_000 + HEARTBEAT_INTERVAL_MS) is not None
    rows = store.recent_heartbeats(1)
    assert len(rows) == 1
    assert rows[0].emitted_at_ms == 1_000 + HEARTBEAT_INTERVAL_MS
    with pytest.raises(ValueError, match="limit must be > 0"):
        store.recent_heartbeats(0)
