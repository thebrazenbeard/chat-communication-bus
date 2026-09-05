"""Durable routing telemetry and 60-second system heartbeat.

Improvements:

Optional multi-thread support (check_same_thread=False) guarded by an RLock.

WAL journal mode for better concurrency.

Atomic update+snapshot in increment().

Index on emitted_at_ms for faster heartbeat lookup.

Typed HeartbeatRecord and helper to read recent heartbeats.

Basic logging for operational visibility.
"""

from future import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
import threading
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(name)

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
source_ref: Optional[str]
provider_state: Optional[str]

def as_dict(self) -> dict[str, Any]:
    return {
        "heartbeat_id": self.heartbeat_id,
        "emitted_at_ms": self.emitted_at_ms,
        "counts": {"routed": self.routed, "dropped": self.dropped, "dlq": self.dlq},
        "source_ref": self.source_ref,
        "provider_state": self.provider_state,
    }

class TelemetryStore:
"""SQLite-backed counters and heartbeat history.

Notes:
- If you plan to use a single TelemetryStore from multiple threads, pass
  check_same_thread=False when constructing the store (defaults to False).
  Access is internally synchronized with an RLock.
- Keep transactions short. emit_heartbeat() uses BEGIN IMMEDIATE to avoid
  duplicate heartbeats within the interval.
"""

def __init__(
    self,
    path: str | Path,
    *,
    timeout: float = 5.0,
    check_same_thread: bool = False,
) -> None:
    self._path = str(path)
    self._lock = threading.RLock()
    # Allow multi-thread use if caller chooses; serialize access with the lock.
    self.connection = sqlite3.connect(
        self._path, timeout=timeout, check_same_thread=check_same_thread
    )
    self.connection.row_factory = sqlite3.Row

    # Tune pragmas for short concurrent write/read patterns.
    try:
        self.connection.execute("PRAGMA journal_mode=WAL")
        # synchronous=FULL is safest but slower; NORMAL is a reasonable tradeoff.
        self.connection.execute("PRAGMA synchronous=NORMAL")
    except Exception:
        # Best-effort; do not fail initialization for environments that restrict PRAGMA.
        logger.exception("Failed to set PRAGMA on telemetry DB")

    with self._lock:
        # Create tables and index.
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
        # Index for fast lookup of the latest heartbeat.
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_telemetry_heartbeats_emitted_at ON radar_telemetry_heartbeats (emitted_at_ms DESC, heartbeat_id DESC)"
        )
        # Ensure counters exist.
        self.connection.executemany(
            "INSERT OR IGNORE INTO radar_telemetry_counters(counter, value) VALUES (?, 0)",
            ((name,) for name in _COUNTER_NAMES),
        )
        self.connection.commit()

def close(self) -> None:
    with self._lock:
        try:
            self.connection.close()
        except Exception:
            logger.exception("Error closing telemetry DB connection")

def increment(self, counter: str, amount: int = 1) -> TelemetrySnapshot:
    """Atomically increment a counter and return the new snapshot.

    The update and snapshot read happen in the same transaction to provide a
    consistent snapshot for callers.
    """
    if counter not in _COUNTER_NAMES:
        raise ValueError("UNKNOWN_TELEMETRY_COUNTER")
    if not isinstance(amount, int) or amount < 0:
        raise ValueError("INVALID_TELEMETRY_INCREMENT")

    with self._lock:
        # Use a transaction so the update and select are atomic.
        # __enter__ on sqlite3.Connection begins a transaction (unless autocommit mode).
        with self.connection:
            self.connection.execute(
                "UPDATE radar_telemetry_counters SET value = value + ? WHERE counter = ?",
                (amount, counter),
            )
            rows = self.connection.execute(
                "SELECT counter, value FROM radar_telemetry_counters"
            ).fetchall()
            values = {row["counter"]: int(row["value"]) for row in rows}
            snapshot = TelemetrySnapshot(*(values[name] for name in _COUNTER_NAMES))
            # transaction will commit on exiting the with-block
    return snapshot

def snapshot(self) -> TelemetrySnapshot:
    """Return a snapshot of counters (not necessarily tied to any transaction)."""
    with self._lock:
        rows = self.connection.execute(
            "SELECT counter, value FROM radar_telemetry_counters"
        ).fetchall()
        values = {row["counter"]: int(row["value"]) for row in rows}
        return TelemetrySnapshot(*(values[name] for name in _COUNTER_NAMES))

def _last_heartbeat_ms(self) -> Optional[int]:
    """Return the timestamp of the last heartbeat, or None if none exist."""
    row = self.connection.execute(
        "SELECT emitted_at_ms FROM radar_telemetry_heartbeats "
        "ORDER BY emitted_at_ms DESC, heartbeat_id DESC LIMIT 1"
    ).fetchone()
    return None if row is None else int(row["emitted_at_ms"])

def emit_heartbeat(
    self,
    now_ms: int,
    *,
    source_ref: Optional[str] = None,
    provider_state: Optional[str] = None,
) -> Dict[str, Any] | None:
    """Emit a telemetry heartbeat if the last heartbeat is older than HEARTBEAT_INTERVAL_MS.

    Returns the telemetry event dict on success, or None if gated by interval.
    """
    if not isinstance(now_ms, int) or now_ms < 0:
        raise ValueError("INVALID_HEARTBEAT_TIME")

    with self._lock:
        # Reserve the database for writing to avoid races between concurrent emitters.
        # BEGIN IMMEDIATE acquires a RESERVED lock and prevents other writers from
        # obtaining a write transaction; read transactions are still allowed.
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            last = self._last_heartbeat_ms()
            if last is not None and now_ms - last < HEARTBEAT_INTERVAL_MS:
                self.connection.rollback()
                return None
            # Read counters inside the same transaction to ensure consistency.
            rows = self.connection.execute(
                "SELECT counter, value FROM radar_telemetry_counters"
            ).fetchall()
            values = {row["counter"]: int(row["value"]) for row in rows}
            snapshot = TelemetrySnapshot(*(values[name] for name in _COUNTER_NAMES))

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
            # Ensure the DB connection is left in a clean state for callers.
            try:
                self.connection.rollback()
            except Exception:
                logger.exception("Failed to rollback telemetry DB after error")
            logger.exception("Failed to emit telemetry heartbeat")
            raise

    return {
        "domain": "system",
        "intent": "telemetry",
        "emitted_at_ms": now_ms,
        "counts": snapshot.as_dict(),
        "source_ref": source_ref,
        "provider_state": provider_state,
    }

def recent_heartbeats(self, limit: int = 100) -> List[HeartbeatRecord]:
    """Return up to `limit` most recent HeartbeatRecord entries."""
    if limit <= 0:
        raise ValueError("limit must be > 0")
    with self._lock:
        rows = self.connection.execute(
            "SELECT heartbeat_id, emitted_at_ms, routed, dropped, dlq, source_ref, provider_state "
            "FROM radar_telemetry_heartbeats "
            "ORDER BY emitted_at_ms DESC, heartbeat_id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            HeartbeatRecord(
                heartbeat_id=int(r["heartbeat_id"]),
                emitted_at_ms=int(r["emitted_at_ms"]),
                routed=int(r["routed"]),
                dropped=int(r["dropped"]),
                dlq=int(r["dlq"]),
                source_ref=r["source_ref"],
                provider_state=r["provider_state"],
            )
            for r in rows
        ]

all = ["HEARTBEAT_INTERVAL_MS", "TelemetrySnapshot", "TelemetryStore", "HeartbeatRecord"]
