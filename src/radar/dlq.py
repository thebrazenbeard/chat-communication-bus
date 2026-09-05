"""Durable SQLite dead-letter queue for Radar."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3


class DeadLetterError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeadLetterItem:
    item_id: int
    message_id: str
    failure_stage: str
    failure_code: str
    envelope: dict[str, object]
    diagnostic: str
    reason_category: str
    source_locator: str | None
    applicability: str
    replay_state: str
    retry_count: int


class DeadLetterStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS radar_dead_letters (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                failure_stage TEXT NOT NULL,
                failure_code TEXT NOT NULL,
                envelope_json TEXT NOT NULL,
                diagnostic TEXT NOT NULL,
                reason_category TEXT NOT NULL DEFAULT 'UNCLASSIFIED',
                source_locator TEXT,
                applicability TEXT NOT NULL DEFAULT 'UNKNOWN'
                    CHECK (applicability IN ('UNKNOWN','APPLICABLE','NOT_APPLICABLE')),
                replay_state TEXT NOT NULL DEFAULT 'PENDING'
                    CHECK (replay_state IN ('PENDING','REPLAYED','DISCARDED')),
                retry_count INTEGER NOT NULL DEFAULT 0 CHECK (retry_count >= 0)
            )
            """
        )
        self._migrate_evidence_columns()
        self.connection.commit()

    def _migrate_evidence_columns(self) -> None:
        columns = {
            row["name"]
            for row in self.connection.execute("PRAGMA table_info(radar_dead_letters)")
        }
        if "reason_category" not in columns:
            self.connection.execute(
                "ALTER TABLE radar_dead_letters "
                "ADD COLUMN reason_category TEXT NOT NULL DEFAULT 'UNCLASSIFIED'"
            )
        if "source_locator" not in columns:
            self.connection.execute(
                "ALTER TABLE radar_dead_letters ADD COLUMN source_locator TEXT"
            )

    def close(self) -> None:
        self.connection.close()

    def record(
        self,
        *,
        message_id: str,
        failure_stage: str,
        failure_code: str,
        envelope: dict[str, object],
        diagnostic: str,
        reason_category: str = "UNCLASSIFIED",
        source_locator: str | None = None,
    ) -> int:
        if not isinstance(reason_category, str) or not reason_category.strip():
            raise DeadLetterError("REASON_CATEGORY_REQUIRED")
        if source_locator is not None and (
            not isinstance(source_locator, str) or not source_locator.strip()
        ):
            raise DeadLetterError("INVALID_SOURCE_LOCATOR")

        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO radar_dead_letters
                    (
                        message_id,
                        failure_stage,
                        failure_code,
                        envelope_json,
                        diagnostic,
                        reason_category,
                        source_locator
                    )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    failure_stage,
                    failure_code,
                    json.dumps(envelope, sort_keys=True, separators=(",", ":")),
                    diagnostic,
                    reason_category.strip().upper(),
                    None if source_locator is None else source_locator.strip(),
                ),
            )
        return int(cursor.lastrowid)

    def inspect(self, item_id: int) -> DeadLetterItem:
        row = self.connection.execute(
            "SELECT * FROM radar_dead_letters WHERE item_id = ?", (item_id,)
        ).fetchone()
        if row is None:
            raise DeadLetterError("NOT_FOUND")
        return DeadLetterItem(
            item_id=int(row["item_id"]),
            message_id=row["message_id"],
            failure_stage=row["failure_stage"],
            failure_code=row["failure_code"],
            envelope=json.loads(row["envelope_json"]),
            diagnostic=row["diagnostic"],
            reason_category=row["reason_category"],
            source_locator=row["source_locator"],
            applicability=row["applicability"],
            replay_state=row["replay_state"],
            retry_count=int(row["retry_count"]),
        )

    def set_applicability(self, item_id: int, applicability: str) -> None:
        if applicability not in {"APPLICABLE", "NOT_APPLICABLE"}:
            raise DeadLetterError("INVALID_APPLICABILITY")
        with self.connection:
            cursor = self.connection.execute(
                "UPDATE radar_dead_letters SET applicability = ? WHERE item_id = ?",
                (applicability, item_id),
            )
        if cursor.rowcount != 1:
            raise DeadLetterError("NOT_FOUND")

    def mark_replay(self, item_id: int) -> None:
        item = self.inspect(item_id)
        if item.applicability == "UNKNOWN":
            raise DeadLetterError("APPLICABILITY_NOT_REFRESHED")
        if item.applicability != "APPLICABLE":
            raise DeadLetterError("MESSAGE_NOT_APPLICABLE")
        with self.connection:
            self.connection.execute(
                """
                UPDATE radar_dead_letters
                SET replay_state = 'REPLAYED', retry_count = retry_count + 1
                WHERE item_id = ?
                """,
                (item_id,),
            )


__all__ = ["DeadLetterError", "DeadLetterItem", "DeadLetterStore"]
