from __future__ import annotations

from radar.envelope import EnvelopeClassification, RadarEnvelope
from radar.heartbeat import HeartbeatRuntime
from radar.telemetry import HEARTBEAT_INTERVAL_MS, TelemetryStore


def test_heartbeat_message_is_radar_background_telemetry(tmp_path):
    store = TelemetryStore(tmp_path / "telemetry.sqlite")
    store.increment("routed", 2)
    store.increment("dropped", 1)
    store.increment("dlq", 3)

    heartbeat = store.emit_heartbeat(1_000)

    assert heartbeat is not None
    assert heartbeat["sender"] == "radar"
    assert heartbeat["domain"] == "system"
    assert heartbeat["intent"] == "telemetry"
    assert heartbeat["priority"] == 4
    assert heartbeat["counts"] == {"routed": 2, "dropped": 1, "dlq": 3}


def test_heartbeat_is_a_canonical_radar_envelope_not_an_out_of_band_shape(tmp_path):
    store = TelemetryStore(tmp_path / "telemetry.sqlite")
    store.increment("routed", 4)

    heartbeat = store.emit_heartbeat(
        1_000,
        source_ref="main@abc",
        provider_state="DEGRADED",
    )

    assert heartbeat is not None
    result = RadarEnvelope.from_mapping(heartbeat)
    assert result.classification is EnvelopeClassification.VALID
    assert result.envelope is not None
    assert result.envelope.message_id == "radar-heartbeat-1000"
    assert result.envelope.created_at == "1970-01-01T00:00:01Z"
    assert result.envelope.audience == ()
    assert result.envelope.priority == 4
    assert result.envelope.payload == {
        "emitted_at_ms": 1_000,
        "counts": {"routed": 4, "dropped": 0, "dlq": 0},
        "source_ref": "main@abc",
        "provider_state": "DEGRADED",
    }


def test_runtime_resumes_from_persisted_due_time_without_sixty_second_lag(tmp_path):
    store = TelemetryStore(tmp_path / "telemetry.sqlite")
    assert store.emit_heartbeat(1_000) is not None

    clock = {"now_ms": 51_000}
    sleeps: list[float] = []
    emitted: list[dict[str, object]] = []

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        clock["now_ms"] += round(seconds * 1_000)

    runtime = HeartbeatRuntime(
        store,
        sink=emitted.append,
        clock_ms=lambda: clock["now_ms"],
        sleep=sleep,
    )
    runtime.run_forever(should_stop=lambda: len(emitted) >= 1)

    assert sleeps == [10.0]
    assert len(emitted) == 1
    assert emitted[0]["emitted_at_ms"] == 1_000 + HEARTBEAT_INTERVAL_MS


def test_runtime_emits_on_exact_sixty_second_cadence_and_stops_cleanly(tmp_path):
    store = TelemetryStore(tmp_path / "telemetry.sqlite")
    clock = {"now_ms": 0}
    emitted: list[dict[str, object]] = []
    sleeps: list[float] = []

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        clock["now_ms"] += round(seconds * 1_000)

    runtime = HeartbeatRuntime(
        store,
        sink=emitted.append,
        clock_ms=lambda: clock["now_ms"],
        sleep=sleep,
        source_ref=lambda: "main@abc",
        provider_state=lambda: "DEGRADED",
    )
    runtime.run_forever(should_stop=lambda: len(emitted) >= 2)

    assert [item["emitted_at_ms"] for item in emitted] == [0, HEARTBEAT_INTERVAL_MS]
    assert sleeps == [60.0]
    assert emitted[-1]["source_ref"] == "main@abc"
    assert emitted[-1]["provider_state"] == "DEGRADED"
