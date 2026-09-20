"""Provider transport intent and observation receipts.

This module performs no network I/O. It binds a prepared adapter request to a
single transport attempt subject and classifies externally observed transport
outcomes without promoting them into provider-consumption or model-behavior claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import json

from .provider_execution_binding import AdapterExecutionPlan
from .provider_openai_compatible import LocalOpenAICompatibleRequest


def _nonempty(value: str, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{label} must be a non-empty exact string")
    return value


def _require_sha256(value: str, label: str) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or any(ch not in "0123456789abcdef" for ch in value)
    ):
        raise ValueError(f"{label} must be lowercase SHA-256")
    return value


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


class TransportState(StrEnum):
    NOT_SENT = "NOT_SENT"
    CONFIRMED_HTTP_RESPONSE = "CONFIRMED_HTTP_RESPONSE"
    REJECTED_HTTP_RESPONSE = "REJECTED_HTTP_RESPONSE"
    UNKNOWN_DELIVERY = "UNKNOWN_DELIVERY"


class RetryPosture(StrEnum):
    NEW_ATTEMPT_REQUIRES_SEPARATE_AUTHORITY = (
        "NEW_ATTEMPT_REQUIRES_SEPARATE_AUTHORITY"
    )
    NO_AUTOMATIC_RETRY = "NO_AUTOMATIC_RETRY"
    READBACK_REQUIRED_NO_BLIND_RETRY = "READBACK_REQUIRED_NO_BLIND_RETRY"


@dataclass(frozen=True)
class TransportIntent:
    attempt_id: str
    plan_digest: str
    envelope_digest: str
    manifest_digest: str
    policy_digest: str
    provider_id: str
    model_id: str
    adapter_version: str
    request_url: str
    request_sha256: str
    intent_claim: str = "TRANSPORT_INTENT_ONLY_NO_SEND_AUTHORITY"

    def __post_init__(self) -> None:
        _nonempty(self.attempt_id, "attempt_id")
        for value, label in (
            (self.plan_digest, "plan_digest"),
            (self.envelope_digest, "envelope_digest"),
            (self.manifest_digest, "manifest_digest"),
            (self.policy_digest, "policy_digest"),
            (self.request_sha256, "request_sha256"),
        ):
            _require_sha256(value, label)
        for value, label in (
            (self.provider_id, "provider_id"),
            (self.model_id, "model_id"),
            (self.adapter_version, "adapter_version"),
            (self.request_url, "request_url"),
        ):
            _nonempty(value, label)
        if self.intent_claim != "TRANSPORT_INTENT_ONLY_NO_SEND_AUTHORITY":
            raise ValueError("unsupported transport intent claim")

    def payload(self) -> dict[str, str]:
        return {
            "schema": "VERA_PROVIDER_TRANSPORT_INTENT_V1",
            "attempt_id": self.attempt_id,
            "plan_digest": self.plan_digest,
            "envelope_digest": self.envelope_digest,
            "manifest_digest": self.manifest_digest,
            "policy_digest": self.policy_digest,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "adapter_version": self.adapter_version,
            "request_url": self.request_url,
            "request_sha256": self.request_sha256,
            "intent_claim": self.intent_claim,
        }

    @property
    def digest(self) -> str:
        return _digest(self.payload())


def build_transport_intent(
    *,
    attempt_id: str,
    plan: AdapterExecutionPlan,
    request: LocalOpenAICompatibleRequest,
) -> TransportIntent:
    if type(plan) is not AdapterExecutionPlan:
        raise ValueError("plan must be exact AdapterExecutionPlan")
    if type(request) is not LocalOpenAICompatibleRequest:
        raise ValueError("request must be exact LocalOpenAICompatibleRequest")
    if (
        request.provider_id != plan.provider_id
        or request.model_id != plan.model_id
        or request.adapter_version != plan.adapter_version
    ):
        raise ValueError("transport request route does not match adapter plan")

    return TransportIntent(
        attempt_id=attempt_id,
        plan_digest=plan.digest,
        envelope_digest=plan.envelope_digest,
        manifest_digest=plan.manifest_digest,
        policy_digest=plan.policy_digest,
        provider_id=plan.provider_id,
        model_id=plan.model_id,
        adapter_version=plan.adapter_version,
        request_url=request.request_url,
        request_sha256=request.payload_sha256,
    )


@dataclass(frozen=True)
class TransportObservation:
    attempt_id: str
    intent_digest: str
    state: TransportState
    http_status: int | None = None
    response_sha256: str | None = None
    observation_claim: str = "EXTERNAL_TRANSPORT_OBSERVATION_ONLY"

    def __post_init__(self) -> None:
        _nonempty(self.attempt_id, "attempt_id")
        _require_sha256(self.intent_digest, "intent_digest")
        if type(self.state) is not TransportState:
            raise ValueError("state must be exact TransportState")
        if self.observation_claim != "EXTERNAL_TRANSPORT_OBSERVATION_ONLY":
            raise ValueError("unsupported transport observation claim")

        if self.state in (TransportState.NOT_SENT, TransportState.UNKNOWN_DELIVERY):
            if self.http_status is not None or self.response_sha256 is not None:
                raise ValueError(
                    f"{self.state.value} cannot carry response evidence"
                )
            return

        if (
            type(self.http_status) is not int
            or isinstance(self.http_status, bool)
            or not 100 <= self.http_status <= 599
        ):
            raise ValueError("HTTP response state requires valid http_status")
        if self.response_sha256 is None:
            raise ValueError("HTTP response state requires response_sha256")
        _require_sha256(self.response_sha256, "response_sha256")

        if self.state is TransportState.CONFIRMED_HTTP_RESPONSE:
            if not 200 <= self.http_status <= 299:
                raise ValueError(
                    "CONFIRMED_HTTP_RESPONSE requires 2xx status"
                )
        elif self.state is TransportState.REJECTED_HTTP_RESPONSE:
            if 200 <= self.http_status <= 299:
                raise ValueError(
                    "REJECTED_HTTP_RESPONSE cannot carry 2xx status"
                )


@dataclass(frozen=True)
class TransportReceipt:
    attempt_id: str
    intent_digest: str
    state: TransportState
    retry_posture: RetryPosture
    http_status: int | None
    response_sha256: str | None
    receipt_claim: str = (
        "TRANSPORT_STATE_ONLY_NOT_PROVIDER_CONSUMPTION_OR_MODEL_BEHAVIOR"
    )

    def __post_init__(self) -> None:
        _nonempty(self.attempt_id, "attempt_id")
        _require_sha256(self.intent_digest, "intent_digest")
        if type(self.state) is not TransportState:
            raise ValueError("state must be exact TransportState")
        if type(self.retry_posture) is not RetryPosture:
            raise ValueError("retry_posture must be exact RetryPosture")
        if self.receipt_claim != (
            "TRANSPORT_STATE_ONLY_NOT_PROVIDER_CONSUMPTION_OR_MODEL_BEHAVIOR"
        ):
            raise ValueError("unsupported transport receipt claim")

        expected = {
            TransportState.NOT_SENT:
                RetryPosture.NEW_ATTEMPT_REQUIRES_SEPARATE_AUTHORITY,
            TransportState.CONFIRMED_HTTP_RESPONSE:
                RetryPosture.NO_AUTOMATIC_RETRY,
            TransportState.REJECTED_HTTP_RESPONSE:
                RetryPosture.NO_AUTOMATIC_RETRY,
            TransportState.UNKNOWN_DELIVERY:
                RetryPosture.READBACK_REQUIRED_NO_BLIND_RETRY,
        }[self.state]
        if self.retry_posture is not expected:
            raise ValueError("retry posture does not match transport state")

        if self.state in (TransportState.NOT_SENT, TransportState.UNKNOWN_DELIVERY):
            if self.http_status is not None or self.response_sha256 is not None:
                raise ValueError(
                    f"{self.state.value} receipt cannot carry response evidence"
                )
        else:
            if (
                type(self.http_status) is not int
                or isinstance(self.http_status, bool)
                or not 100 <= self.http_status <= 599
            ):
                raise ValueError("HTTP response receipt requires valid status")
            if self.response_sha256 is None:
                raise ValueError("HTTP response receipt requires response digest")
            _require_sha256(self.response_sha256, "response_sha256")


def record_transport_observation(
    *,
    intent: TransportIntent,
    observation: TransportObservation,
) -> TransportReceipt:
    if type(intent) is not TransportIntent:
        raise ValueError("intent must be exact TransportIntent")
    if type(observation) is not TransportObservation:
        raise ValueError("observation must be exact TransportObservation")
    if observation.attempt_id != intent.attempt_id:
        raise ValueError("transport observation attempt mismatch")
    if observation.intent_digest != intent.digest:
        raise ValueError("transport observation intent mismatch")

    posture = {
        TransportState.NOT_SENT:
            RetryPosture.NEW_ATTEMPT_REQUIRES_SEPARATE_AUTHORITY,
        TransportState.CONFIRMED_HTTP_RESPONSE:
            RetryPosture.NO_AUTOMATIC_RETRY,
        TransportState.REJECTED_HTTP_RESPONSE:
            RetryPosture.NO_AUTOMATIC_RETRY,
        TransportState.UNKNOWN_DELIVERY:
            RetryPosture.READBACK_REQUIRED_NO_BLIND_RETRY,
    }[observation.state]

    return TransportReceipt(
        attempt_id=intent.attempt_id,
        intent_digest=intent.digest,
        state=observation.state,
        retry_posture=posture,
        http_status=observation.http_status,
        response_sha256=observation.response_sha256,
    )


__all__ = [
    "RetryPosture",
    "TransportIntent",
    "TransportObservation",
    "TransportReceipt",
    "TransportState",
    "build_transport_intent",
    "record_transport_observation",
]
