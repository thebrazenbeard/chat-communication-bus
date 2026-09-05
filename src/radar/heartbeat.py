"""Runtime scheduler for Radar's durable 60-second telemetry heartbeat."""

from __future__ import annotations

from collections.abc import Callable
import time

from .telemetry import TelemetryStore


HeartbeatMessage = dict[str, object]
HeartbeatSink = Callable[[HeartbeatMessage], None]
EvidenceSource = str | None | Callable[[], str | None]


def _resolve_evidence(value: EvidenceSource) -> str | None:
    return value() if callable(value) else value


class HeartbeatRuntime:
    """Drive ``TelemetryStore`` heartbeats at the persisted exact due time.

    Clock and sleep functions are injectable so replay and tests remain fully
    deterministic. The scheduler consults durable heartbeat history before every
    sleep, so restarting inside the 60-second window waits only for the remaining
    interval rather than adding a fresh 60-second delay.
    """

    def __init__(
        self,
        store: TelemetryStore,
        *,
        sink: HeartbeatSink,
        clock_ms: Callable[[], int] | None = None,
        sleep: Callable[[float], None] | None = None,
        source_ref: EvidenceSource = None,
        provider_state: EvidenceSource = None,
    ) -> None:
        self.store = store
        self.sink = sink
        self.clock_ms = clock_ms or (lambda: time.time_ns() // 1_000_000)
        self.sleep = sleep or time.sleep
        self.source_ref = source_ref
        self.provider_state = provider_state

    def tick(self) -> HeartbeatMessage | None:
        """Emit one heartbeat if due and return the emitted message."""
        heartbeat = self.store.emit_heartbeat(
            self.clock_ms(),
            source_ref=_resolve_evidence(self.source_ref),
            provider_state=_resolve_evidence(self.provider_state),
        )
        if heartbeat is not None:
            self.sink(heartbeat)
        return heartbeat

    def run_forever(self, *, should_stop: Callable[[], bool] | None = None) -> None:
        """Run until ``should_stop`` returns true.

        The stop predicate is checked both before work and immediately after an
        emission so a caller can terminate without an unnecessary final sleep.
        """
        stop = should_stop or (lambda: False)
        while not stop():
            self.tick()
            if stop():
                return

            delay_ms = self.store.milliseconds_until_heartbeat(self.clock_ms())
            if delay_ms > 0:
                self.sleep(delay_ms / 1_000)


__all__ = ["HeartbeatMessage", "HeartbeatRuntime", "HeartbeatSink"]
