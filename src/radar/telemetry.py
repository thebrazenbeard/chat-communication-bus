"""Durable routing telemetry and 60-second system heartbeat."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import sqlite3
import threading
from typing import Any


logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL_MS = 60_000
_COUNTER_NAMES = ("routed", "dropped", "dlq")


@dataclass(frozen=True)
class TelemetrySnapshot:
    routed: int
    dropped: int
    dlq: int

    def as_dict(self) -> dict[str, int]:
        return {"routed": self.routed, "dropped": self.dropped, "dlq": self.dlq}


@dataclass(frozen=True)
class HeartbeatRecord:
    heartbeat_id: int
    emitted_at_ms: int
    routed: int
    dropped: int
    dlq: int
    source_ref: str | None
    provider_state: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "heartbeat_id": self.heartbeat_id,
            "emitted_at_ms": self.emitted_at_ms,
            "counts": {
                "routed": self.routed,
                "dropped": self.dropped,
                "dlq": self.dlq,
            },
            "source_ref": self.source_ref,
            "provider_state": self.provider_state,
        }


class TelemetryStore:
    """SQLite-backed counters and heartbeat history.

    Thread sharing is explicit. SQLite's default same-thread protection remains
    enabled unless a caller deliberately opts out; an RLock serializes this
    object's access when a shared connection is requested.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        timeout: float = 5.0,
        check_same_thread: bool = True,
    ) -> None:
        self._path = str(path)
        self._lock = threading.RLock()
        self.connection = sqlite3.connect(
            self._path,
            timeout=timeout,
            check_same_thread=check_same_thread,
        )
        self.connection.row_factory = sqlite3.Row

        # WAL improves reader/writer coexistence for file-backed stores. It is an
        # optimization, not a durability downgrade: FULL synchronous remains a
        # required invariant even when WAL cannot be enabled by the environment.
        try:
            self.connection.execute("PRAGMA journal_mode=WAL")
        except sqlite3.DatabaseError:
            logger.warning("WAL journal mode unavailable for telemetry DB", exc_info=True)
        self.connection.execute("PRAGMA synchronous=FULL")

        with self._lock:
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
            self.connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_telemetry_heartbeats_emitted_at "
                "ON radar_telemetry_heartbeats (emitted_at_ms DESC, heartbeat_id DESC)"
            )
            self.connection.executemany(
                "INSERT OR IGNORE INTO radar_telemetry_counters(counter, value) VALUES (?, 0)",
                ((name,) for name in _COUNTER_NAMES),
            )
            self.connection.commit()

    def close(self) -> None:
        with self._lock:
            self.connection.close()

    def increment(self, counter: str, amount: int = 1) -> TelemetrySnapshot:
        """Atomically increment a counter and return the resulting snapshot."""
        if counter not in _COUNTER_NAMES:
            raise ValueError("UNKNOWN_TELEMETRY_COUNTER")
        if type(amount) is not int or amount < 0:
            raise ValueError("INVALID_TELEMETRY_INCREMENT")

        with self._lock:
            with self.connection:
                self.connection.execute(
                    "UPDATE radar_telemetry_counters SET value = value + ? WHERE counter = ?",
                    (amount, counter),
                )
                return self._snapshot_unlocked()

    def snapshot(self) -> TelemetrySnapshot:
        with self._lock:
            return self._snapshot_unlocked()

    def _snapshot_unlocked(self) -> TelemetrySnapshot:
        rows = self.connection.execute(
            "SELECT counter, value FROM radar_telemetry_counters"
        ).fetchall()
        values = {row["counter"]: int(row["value"]) for row in rows}
        try:
            return TelemetrySnapshot(*(values[name] for name in _COUNTER_NAMES))
        except KeyError as exc:
            raise RuntimeError("TELEMETRY_COUNTER_STATE_INCOMPLETE") from exc

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
        """Insert one heartbeat when the 60-second interval is due.

        ``now_ms`` is supplied by the scheduler/runtime so tests and replay are
        deterministic. A clock regression is an error rather than being
        misinterpreted as a heartbeat still inside the previous interval.
        """
        if type(now_ms) is not int or now_ms < 0:
            raise ValueError("INVALID_HEARTBEAT_TIME")

        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                last = self._last_heartbeat_ms()
                if last is not None and now_ms < last:
                    raise ValueError("HEARTBEAT_CLOCK_REGRESSION")
                if last is not None and now_ms - last < HEARTBEAT_INTERVAL_MS:
                    self.connection.rollback()
                    return None

                snapshot = self._snapshot_unlocked()
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
                if self.connection.in_transaction:
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

    def recent_heartbeats(self, limit: int = 100) -> list[HeartbeatRecord]:
        if type(limit) is not int or limit <= 0:
            raise ValueError("limit must be > 0")
        with self._lock:
            rows = self.connection.execute(
                "SELECT heartbeat_id, emitted_at_ms, routed, dropped, dlq, "
                "source_ref, provider_state FROM radar_telemetry_heartbeats "
                "ORDER BY emitted_at_ms DESC, heartbeat_id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [
                HeartbeatRecord(
                    heartbeat_id=int(row["heartbeat_id"]),
                    emitted_at_ms=int(row["emitted_at_ms"]),
                    routed=int(row["routed"]),
                    dropped=int(row["dropped"]),
                    dlq=int(row["dlq"]),
                    source_ref=row["source_ref"],
                    provider_state=row["provider_state"],
                )
                for row in rows
            ]


__all__ = [
    "HEARTBEAT_INTERVAL_MS",
    "HeartbeatRecord",
    "TelemetrySnapshot",
    "TelemetryStore",
]
