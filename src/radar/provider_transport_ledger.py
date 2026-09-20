"""Durable provider-transport attempt ledger.

The ledger performs no network I/O. It gives transport attempt ids durable,
cross-process meaning and prevents a new registration for the same exact
provider/request subject while a prior UNKNOWN_DELIVERY remains unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3

from .provider_transport import (
    TransportIntent,
    TransportObservation,
    TransportReceipt,
    TransportState,
    record_transport_observation,
)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS transport_attempts (
    attempt_id TEXT PRIMARY KEY,
    intent_digest TEXT NOT NULL,
    plan_digest TEXT NOT NULL,
    envelope_digest TEXT NOT NULL,
    manifest_digest TEXT NOT NULL,
    policy_digest TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    adapter_version TEXT NOT NULL,
    request_url TEXT NOT NULL,
    request_sha256 TEXT NOT NULL,
    intent_claim TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transport_observations (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id TEXT NOT NULL,
    intent_digest TEXT NOT NULL,
    state TEXT NOT NULL,
    retry_posture TEXT NOT NULL,
    http_status INTEGER,
    response_sha256 TEXT,
    receipt_claim TEXT NOT NULL,
    FOREIGN KEY (attempt_id) REFERENCES transport_attempts(attempt_id)
);

CREATE INDEX IF NOT EXISTS idx_transport_observations_attempt_sequence
    ON transport_observations(attempt_id, sequence);

CREATE INDEX IF NOT EXISTS idx_transport_attempt_request_subject
    ON transport_attempts(
        provider_id,
        model_id,
        adapter_version,
        request_url,
        request_sha256
    );
"""


@dataclass(frozen=True)
class AttemptRegistration:
    created: bool
    intent: TransportIntent

    def __post_init__(self) -> None:
        if type(self.created) is not bool:
            raise ValueError("created must be exact bool")
        if type(self.intent) is not TransportIntent:
            raise ValueError("intent must be exact TransportIntent")


@dataclass(frozen=True)
class ObservationCommit:
    created: bool
    sequence: int
    receipt: TransportReceipt

    def __post_init__(self) -> None:
        if type(self.created) is not bool:
            raise ValueError("created must be exact bool")
        if (
            type(self.sequence) is not int
            or isinstance(self.sequence, bool)
            or self.sequence <= 0
        ):
            raise ValueError("sequence must be positive exact int")
        if type(self.receipt) is not TransportReceipt:
            raise ValueError("receipt must be exact TransportReceipt")


class TransportLedger:
    """SQLite-backed immutable attempt registration and observation history."""

    __slots__ = ("_path",)

    def __init__(self, path: str) -> None:
        if type(path) is not str or not path.strip():
            raise ValueError("path must be a non-empty exact string")
        self._path = path
        with self._connect() as connection:
            connection.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self._path,
            timeout=10.0,
            isolation_level=None,
        )
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    @staticmethod
    def _intent_values(intent: TransportIntent) -> tuple[object, ...]:
        return (
            intent.attempt_id,
            intent.digest,
            intent.plan_digest,
            intent.envelope_digest,
            intent.manifest_digest,
            intent.policy_digest,
            intent.provider_id,
            intent.model_id,
            intent.adapter_version,
            intent.request_url,
            intent.request_sha256,
            intent.intent_claim,
        )

    @staticmethod
    def _row_to_intent(row: sqlite3.Row | tuple[object, ...]) -> TransportIntent:
        return TransportIntent(
            attempt_id=str(row[0]),
            plan_digest=str(row[2]),
            envelope_digest=str(row[3]),
            manifest_digest=str(row[4]),
            policy_digest=str(row[5]),
            provider_id=str(row[6]),
            model_id=str(row[7]),
            adapter_version=str(row[8]),
            request_url=str(row[9]),
            request_sha256=str(row[10]),
            intent_claim=str(row[11]),
        )

    @staticmethod
    def _assert_intent_row_matches(
        row: sqlite3.Row | tuple[object, ...],
        intent: TransportIntent,
    ) -> None:
        readback = TransportLedger._row_to_intent(row)
        if readback != intent or str(row[1]) != intent.digest:
            raise ValueError("durable attempt registration diverges from intent")

    def register_intent(self, intent: TransportIntent) -> AttemptRegistration:
        if type(intent) is not TransportIntent:
            raise ValueError("intent must be exact TransportIntent")

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                """
                SELECT attempt_id, intent_digest, plan_digest, envelope_digest,
                       manifest_digest, policy_digest, provider_id, model_id,
                       adapter_version, request_url, request_sha256, intent_claim
                  FROM transport_attempts
                 WHERE attempt_id = ?
                """,
                (intent.attempt_id,),
            ).fetchone()
            if existing is not None:
                self._assert_intent_row_matches(existing, intent)
                connection.execute("COMMIT")
                return AttemptRegistration(created=False, intent=intent)

            unresolved = connection.execute(
                """
                SELECT a.attempt_id
                  FROM transport_attempts AS a
                  JOIN transport_observations AS o
                    ON o.sequence = (
                        SELECT MAX(o2.sequence)
                          FROM transport_observations AS o2
                         WHERE o2.attempt_id = a.attempt_id
                    )
                 WHERE a.provider_id = ?
                   AND a.model_id = ?
                   AND a.adapter_version = ?
                   AND a.request_url = ?
                   AND a.request_sha256 = ?
                   AND o.state = ?
                 LIMIT 1
                """,
                (
                    intent.provider_id,
                    intent.model_id,
                    intent.adapter_version,
                    intent.request_url,
                    intent.request_sha256,
                    TransportState.UNKNOWN_DELIVERY.value,
                ),
            ).fetchone()
            if unresolved is not None:
                raise ValueError(
                    "unresolved UNKNOWN_DELIVERY blocks new attempt registration"
                )

            connection.execute(
                """
                INSERT INTO transport_attempts (
                    attempt_id, intent_digest, plan_digest, envelope_digest,
                    manifest_digest, policy_digest, provider_id, model_id,
                    adapter_version, request_url, request_sha256, intent_claim
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._intent_values(intent),
            )
            readback = connection.execute(
                """
                SELECT attempt_id, intent_digest, plan_digest, envelope_digest,
                       manifest_digest, policy_digest, provider_id, model_id,
                       adapter_version, request_url, request_sha256, intent_claim
                  FROM transport_attempts
                 WHERE attempt_id = ?
                """,
                (intent.attempt_id,),
            ).fetchone()
            if readback is None:
                raise ValueError("attempt registration readback missing")
            self._assert_intent_row_matches(readback, intent)
            connection.execute("COMMIT")
            return AttemptRegistration(created=True, intent=intent)
        except Exception:
            try:
                connection.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        finally:
            connection.close()

    def get_intent(self, attempt_id: str) -> TransportIntent | None:
        if type(attempt_id) is not str or not attempt_id.strip():
            raise ValueError("attempt_id must be a non-empty exact string")
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT attempt_id, intent_digest, plan_digest, envelope_digest,
                       manifest_digest, policy_digest, provider_id, model_id,
                       adapter_version, request_url, request_sha256, intent_claim
                  FROM transport_attempts
                 WHERE attempt_id = ?
                """,
                (attempt_id,),
            ).fetchone()
        if row is None:
            return None
        intent = self._row_to_intent(row)
        self._assert_intent_row_matches(row, intent)
        return intent

    @staticmethod
    def _row_to_receipt(row: sqlite3.Row | tuple[object, ...]) -> TransportReceipt:
        return TransportReceipt(
            attempt_id=str(row[1]),
            intent_digest=str(row[2]),
            state=TransportState(str(row[3])),
            retry_posture=__import__(
                "radar.provider_transport",
                fromlist=["RetryPosture"],
            ).RetryPosture(str(row[4])),
            http_status=None if row[5] is None else int(row[5]),
            response_sha256=None if row[6] is None else str(row[6]),
            receipt_claim=str(row[7]),
        )

    def commit_observation(
        self,
        *,
        intent: TransportIntent,
        observation: TransportObservation,
    ) -> ObservationCommit:
        if type(intent) is not TransportIntent:
            raise ValueError("intent must be exact TransportIntent")
        if type(observation) is not TransportObservation:
            raise ValueError("observation must be exact TransportObservation")

        candidate = record_transport_observation(
            intent=intent,
            observation=observation,
        )

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            attempt = connection.execute(
                """
                SELECT attempt_id, intent_digest, plan_digest, envelope_digest,
                       manifest_digest, policy_digest, provider_id, model_id,
                       adapter_version, request_url, request_sha256, intent_claim
                  FROM transport_attempts
                 WHERE attempt_id = ?
                """,
                (intent.attempt_id,),
            ).fetchone()
            if attempt is None:
                raise ValueError("transport attempt is not registered")
            self._assert_intent_row_matches(attempt, intent)

            latest = connection.execute(
                """
                SELECT sequence, attempt_id, intent_digest, state, retry_posture,
                       http_status, response_sha256, receipt_claim
                  FROM transport_observations
                 WHERE attempt_id = ?
                 ORDER BY sequence DESC
                 LIMIT 1
                """,
                (intent.attempt_id,),
            ).fetchone()

            if latest is not None:
                current = self._row_to_receipt(latest)
                if current == candidate:
                    connection.execute("COMMIT")
                    return ObservationCommit(
                        created=False,
                        sequence=int(latest[0]),
                        receipt=current,
                    )
                if current.state is not TransportState.UNKNOWN_DELIVERY:
                    raise ValueError(
                        "final transport state already recorded for attempt"
                    )
                if candidate.state is TransportState.UNKNOWN_DELIVERY:
                    raise ValueError(
                        "divergent UNKNOWN_DELIVERY observation is not allowed"
                    )

            cursor = connection.execute(
                """
                INSERT INTO transport_observations (
                    attempt_id, intent_digest, state, retry_posture,
                    http_status, response_sha256, receipt_claim
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.attempt_id,
                    candidate.intent_digest,
                    candidate.state.value,
                    candidate.retry_posture.value,
                    candidate.http_status,
                    candidate.response_sha256,
                    candidate.receipt_claim,
                ),
            )
            sequence = int(cursor.lastrowid)
            readback = connection.execute(
                """
                SELECT sequence, attempt_id, intent_digest, state, retry_posture,
                       http_status, response_sha256, receipt_claim
                  FROM transport_observations
                 WHERE sequence = ?
                """,
                (sequence,),
            ).fetchone()
            if readback is None:
                raise ValueError("transport observation readback missing")
            receipt = self._row_to_receipt(readback)
            if receipt != candidate:
                raise ValueError("transport observation readback diverged")
            connection.execute("COMMIT")
            return ObservationCommit(
                created=True,
                sequence=sequence,
                receipt=receipt,
            )
        except Exception:
            try:
                connection.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        finally:
            connection.close()

    def latest_receipt(self, attempt_id: str) -> TransportReceipt | None:
        if type(attempt_id) is not str or not attempt_id.strip():
            raise ValueError("attempt_id must be a non-empty exact string")
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT sequence, attempt_id, intent_digest, state, retry_posture,
                       http_status, response_sha256, receipt_claim
                  FROM transport_observations
                 WHERE attempt_id = ?
                 ORDER BY sequence DESC
                 LIMIT 1
                """,
                (attempt_id,),
            ).fetchone()
        return None if row is None else self._row_to_receipt(row)

    def observation_history(self, attempt_id: str) -> tuple[TransportReceipt, ...]:
        if type(attempt_id) is not str or not attempt_id.strip():
            raise ValueError("attempt_id must be a non-empty exact string")
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT sequence, attempt_id, intent_digest, state, retry_posture,
                       http_status, response_sha256, receipt_claim
                  FROM transport_observations
                 WHERE attempt_id = ?
                 ORDER BY sequence ASC
                """,
                (attempt_id,),
            ).fetchall()
        return tuple(self._row_to_receipt(row) for row in rows)


__all__ = [
    "AttemptRegistration",
    "ObservationCommit",
    "TransportLedger",
]
