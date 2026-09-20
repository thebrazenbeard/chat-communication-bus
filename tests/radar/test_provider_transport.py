from dataclasses import replace
from hashlib import sha256
import json

import pytest

from radar.provider_execution_binding import AdapterExecutionPlan
from radar.provider_openai_compatible import LocalOpenAICompatibleRequest
from radar.provider_routing import RouteSelectionState
from radar.provider_transport import (
    RetryPosture,
    TransportObservation,
    TransportState,
    build_transport_intent,
    record_transport_observation,
)


def digest(label: str) -> str:
    return sha256(label.encode("utf-8")).hexdigest()


def plan(
    *,
    provider="ollama",
    model="local-model",
    adapter="openai-compatible-chat-v1",
) -> AdapterExecutionPlan:
    return AdapterExecutionPlan(
        envelope_digest=digest("envelope"),
        manifest_digest=digest("manifest"),
        policy_digest=digest("policy"),
        provider_id=provider,
        model_id=model,
        adapter_version=adapter,
        route_state=RouteSelectionState.SELECTED_ELIGIBLE,
        instruction_sha256=digest("instructions"),
        input_sha256=digest("input"),
        state_blobs=("a" * 40,),
        prohibited_effects=("MERGE",),
        authority_scope=("READ_GITHUB",),
    )


def request(
    *,
    provider="ollama",
    model="local-model",
    adapter="openai-compatible-chat-v1",
) -> LocalOpenAICompatibleRequest:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "instructions"},
            {"role": "user", "content": "reference"},
        ],
        "stream": False,
    }
    payload_json = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return LocalOpenAICompatibleRequest(
        provider_id=provider,
        model_id=model,
        adapter_version=adapter,
        request_url="http://127.0.0.1:11434/v1/chat/completions",
        payload_json=payload_json,
        payload_sha256=sha256(payload_json.encode("utf-8")).hexdigest(),
    )


def intent():
    return build_transport_intent(
        attempt_id="attempt-001",
        plan=plan(),
        request=request(),
    )


def test_transport_intent_binds_exact_plan_route_and_request():
    p = plan()
    r = request()
    i = build_transport_intent(
        attempt_id="attempt-001",
        plan=p,
        request=r,
    )
    assert i.plan_digest == p.digest
    assert i.envelope_digest == p.envelope_digest
    assert i.manifest_digest == p.manifest_digest
    assert i.policy_digest == p.policy_digest
    assert i.request_sha256 == r.payload_sha256
    assert i.request_url == r.request_url
    assert i.intent_claim == "TRANSPORT_INTENT_ONLY_NO_SEND_AUTHORITY"


def test_transport_intent_rejects_route_substitution():
    with pytest.raises(ValueError, match="route"):
        build_transport_intent(
            attempt_id="attempt-001",
            plan=plan(),
            request=request(provider="lmstudio"),
        )


def test_unknown_delivery_cannot_carry_response_evidence():
    i = intent()
    with pytest.raises(ValueError, match="cannot carry response evidence"):
        TransportObservation(
            attempt_id=i.attempt_id,
            intent_digest=i.digest,
            state=TransportState.UNKNOWN_DELIVERY,
            http_status=200,
            response_sha256=digest("response"),
        )


def test_confirmed_response_requires_2xx_and_response_digest():
    i = intent()
    with pytest.raises(ValueError, match="requires 2xx"):
        TransportObservation(
            attempt_id=i.attempt_id,
            intent_digest=i.digest,
            state=TransportState.CONFIRMED_HTTP_RESPONSE,
            http_status=500,
            response_sha256=digest("response"),
        )
    with pytest.raises(ValueError, match="requires response_sha256"):
        TransportObservation(
            attempt_id=i.attempt_id,
            intent_digest=i.digest,
            state=TransportState.CONFIRMED_HTTP_RESPONSE,
            http_status=200,
        )


def test_rejected_response_cannot_carry_2xx():
    i = intent()
    with pytest.raises(ValueError, match="cannot carry 2xx"):
        TransportObservation(
            attempt_id=i.attempt_id,
            intent_digest=i.digest,
            state=TransportState.REJECTED_HTTP_RESPONSE,
            http_status=204,
            response_sha256=digest("response"),
        )


def test_observation_must_bind_exact_attempt_and_intent():
    i = intent()
    wrong_attempt = TransportObservation(
        attempt_id="attempt-other",
        intent_digest=i.digest,
        state=TransportState.NOT_SENT,
    )
    with pytest.raises(ValueError, match="attempt mismatch"):
        record_transport_observation(intent=i, observation=wrong_attempt)

    wrong_intent = TransportObservation(
        attempt_id=i.attempt_id,
        intent_digest=digest("other-intent"),
        state=TransportState.NOT_SENT,
    )
    with pytest.raises(ValueError, match="intent mismatch"):
        record_transport_observation(intent=i, observation=wrong_intent)


def test_unknown_delivery_requires_readback_and_forbids_blind_retry():
    i = intent()
    observation = TransportObservation(
        attempt_id=i.attempt_id,
        intent_digest=i.digest,
        state=TransportState.UNKNOWN_DELIVERY,
    )
    receipt = record_transport_observation(intent=i, observation=observation)
    assert receipt.retry_posture is RetryPosture.READBACK_REQUIRED_NO_BLIND_RETRY
    assert receipt.http_status is None
    assert receipt.response_sha256 is None


def test_not_sent_does_not_itself_authorize_a_new_attempt():
    i = intent()
    receipt = record_transport_observation(
        intent=i,
        observation=TransportObservation(
            attempt_id=i.attempt_id,
            intent_digest=i.digest,
            state=TransportState.NOT_SENT,
        ),
    )
    assert (
        receipt.retry_posture
        is RetryPosture.NEW_ATTEMPT_REQUIRES_SEPARATE_AUTHORITY
    )


@pytest.mark.parametrize(
    ("state", "status"),
    [
        (TransportState.CONFIRMED_HTTP_RESPONSE, 200),
        (TransportState.REJECTED_HTTP_RESPONSE, 429),
        (TransportState.REJECTED_HTTP_RESPONSE, 500),
    ],
)
def test_http_response_states_never_auto_retry(state, status):
    i = intent()
    receipt = record_transport_observation(
        intent=i,
        observation=TransportObservation(
            attempt_id=i.attempt_id,
            intent_digest=i.digest,
            state=state,
            http_status=status,
            response_sha256=digest(f"response-{status}"),
        ),
    )
    assert receipt.retry_posture is RetryPosture.NO_AUTOMATIC_RETRY


def test_receipt_retry_posture_cannot_be_manually_rebound():
    i = intent()
    receipt = record_transport_observation(
        intent=i,
        observation=TransportObservation(
            attempt_id=i.attempt_id,
            intent_digest=i.digest,
            state=TransportState.UNKNOWN_DELIVERY,
        ),
    )
    with pytest.raises(ValueError, match="retry posture"):
        replace(
            receipt,
            retry_posture=RetryPosture.NO_AUTOMATIC_RETRY,
        )


def test_transport_receipt_does_not_claim_provider_consumption_or_behavior():
    i = intent()
    receipt = record_transport_observation(
        intent=i,
        observation=TransportObservation(
            attempt_id=i.attempt_id,
            intent_digest=i.digest,
            state=TransportState.CONFIRMED_HTTP_RESPONSE,
            http_status=200,
            response_sha256=digest("response"),
        ),
    )
    assert receipt.receipt_claim == (
        "TRANSPORT_STATE_ONLY_NOT_PROVIDER_CONSUMPTION_OR_MODEL_BEHAVIOR"
    )
    assert not hasattr(receipt, "provider_consumed")
    assert not hasattr(receipt, "model_obeyed")
