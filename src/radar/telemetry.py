"""Durable routing telemetry and 60-second system heartbeat."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
from typing import Mapping


HEARTBEAT_INTERVAL_MS = 60_000
_COUNTER_NAMES = ("routed", "dropped", "dlq")


@dataclass(frozen=True)
class TelemetrySnapshot:
    routed: int
    dropped: int
    dlq: int

    def as_dict(self) -> dict[str, int]:
        return {
            "routed": self.routed,
            "dropped": self.dropped,
            "dlq": self.dlq,
        }


class TelemetryStore:
    """SQLite-backed counters and heartbeat history.

    A single immediate transaction makes the interval check and heartbeat insert
    atomic, so concurrent emitters cannot publish duplicate heartbeats.
    """

    def __init__(self, path: str | Path) -> None:
        self.connection = sqlite3.connect(str(path), timeout=5)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS radar_telemetry_counters (
                counter TEXT PRIMARY KEY,
                value INTEGER NOT NULL CHECK (value >= 0)
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS radar_telemetry_heartbeats (
                heartbeat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emitted_at_ms INTEGER NOT NULL,
                routed INTEGER NOT NULL,
                dropped INTEGER NOT NULL,
                dlq INTEGER NOT NULL,
                source_ref TEXT,
                provider_state TEXT
            )
            """
        )
        self.connection.executemany(
            "INSERT OR IGNORE INTO radar_telemetry_counters(counter, value) VALUES (?, 0)",
            ((name,) for name in _COUNTER_NAMES),
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def increment(self, counter: str, amount: int = 1) -> TelemetrySnapshot:
        if counter not in _COUNTER_NAMES:
            raise ValueError("UNKNOWN_TELEMETRY_COUNTER")
        if not isinstance(amount, int) or amount < 0:
            raise ValueError("INVALID_TELEMETRY_INCREMENT")
        with self.connection:
            self.connection.execute(
                "UPDATE radar_telemetry_counters SET value = value + ? WHERE counter = ?",
                (amount, counter),
            )
        return self.snapshot()

    def snapshot(self) -> TelemetrySnapshot:
        rows = self.connection.execute(
            "SELECT counter, value FROM radar_telemetry_counters"
        ).fetchall()
        values = {row["counter"]: int(row["value"]) for row in rows}
        return TelemetrySnapshot(*(values[name] for name in _COUNTER_NAMES))

    def _last_heartbeat_ms(self) -> int | None:
        row = self.connection.execute(
            "SELECT emitted_at_ms FROM radar_telemetry_heartbeats "
            "ORDER BY emitted_at_ms DESC, heartbeat_id DESC LIMIT 1"
        ).fetchone()
        return None if row is None else int(row["emitted_at_ms"])

    def emit_heartbeat(
        self,
        now_ms: int,
        *,
        source_ref: str | None = None,
        provider_state: str | None = None,
    ) -> dict[str, object] | None:
        if not isinstance(now_ms, int) or now_ms < 0:
            raise ValueError("INVALID_HEARTBEAT_TIME")

        self.connection.execute("BEGIN IMMEDIATE")
        try:
            last = self._last_heartbeat_ms()
            if last is not None and now_ms - last < HEARTBEAT_INTERVAL_MS:
                self.connection.rollback()
                return None
            snapshot = self.snapshot()
            self.connection.execute(
                """
                INSERT INTO radar_telemetry_heartbeats
                    (emitted_at_ms, routed, dropped, dlq, source_ref, provider_state)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    now_ms,
                    snapshot.routed,
                    snapshot.dropped,
                    snapshot.dlq,
                    source_ref,
                    provider_state,
                ),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

        return {
            "domain": "system",
            "intent": "telemetry",
            "emitted_at_ms": now_ms,
            "counts": snapshot.as_dict(),
            "source_ref": source_ref,
            "provider_state": provider_state,
        }


__all__ = ["HEARTBEAT_INTERVAL_MS", "TelemetrySnapshot", "TelemetryStore"]
