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
    try:
        store.increment("unknown")
    except ValueError as exc:
        assert str(exc) == "UNKNOWN_TELEMETRY_COUNTER"
    else:
        raise AssertionError("unknown counter accepted")
    try:
        store.emit_heartbeat(-1)
    except ValueError as exc:
        assert str(exc) == "INVALID_HEARTBEAT_TIME"
    else:
        raise AssertionError("negative heartbeat time accepted")
