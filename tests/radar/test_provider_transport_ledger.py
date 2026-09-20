from dataclasses import replace
from hashlib import sha256

import pytest

from radar.provider_transport import (
    RetryPosture,
    TransportIntent,
    TransportObservation,
    TransportState,
)
from radar.provider_transport_ledger import TransportLedger


def digest(label: str) -> str:
    return sha256(label.encode("utf-8")).hexdigest()


def intent(
    attempt_id: str,
    *,
    request_sha256: str | None = None,
    provider="ollama",
    model="local-model",
    adapter="openai-compatible-chat-v1",
    url="http://127.0.0.1:11434/v1/chat/completions",
) -> TransportIntent:
    return TransportIntent(
        attempt_id=attempt_id,
        plan_digest=digest(f"plan-{attempt_id}"),
        envelope_digest=digest("envelope"),
        manifest_digest=digest(f"manifest-{provider}-{model}-{adapter}"),
        policy_digest=digest("policy"),
        provider_id=provider,
        model_id=model,
        adapter_version=adapter,
        request_url=url,
        request_sha256=request_sha256 or digest("same-request"),
    )


def observation(
    i: TransportIntent,
    state: TransportState,
    *,
    status: int | None = None,
    response: str | None = None,
) -> TransportObservation:
    return TransportObservation(
        attempt_id=i.attempt_id,
        intent_digest=i.digest,
        state=state,
        http_status=status,
        response_sha256=None if response is None else digest(response),
    )


def ledger(tmp_path) -> TransportLedger:
    return TransportLedger(str(tmp_path / "transport.db"))


def test_registration_persists_across_reopen(tmp_path):
    path = str(tmp_path / "transport.db")
    first = TransportLedger(path)
    i = intent("attempt-a")
    result = first.register_intent(i)
    assert result.created is True

    reopened = TransportLedger(path)
    assert reopened.get_intent(i.attempt_id) == i


def test_same_attempt_registration_is_idempotent(tmp_path):
    store = ledger(tmp_path)
    i = intent("attempt-a")
    assert store.register_intent(i).created is True
    assert store.register_intent(i).created is False


def test_attempt_id_collision_with_different_intent_fails_closed(tmp_path):
    store = ledger(tmp_path)
    i = intent("attempt-a")
    store.register_intent(i)
    divergent = replace(i, request_sha256=digest("different"))
    with pytest.raises(ValueError, match="diverges"):
        store.register_intent(divergent)


def test_unobserved_attempt_makes_exact_request_subject_single_flight(tmp_path):
    store = ledger(tmp_path)
    first = intent("attempt-a")
    second = intent("attempt-b")
    store.register_intent(first)
    with pytest.raises(ValueError, match="unresolved transport attempt"):
        store.register_intent(second)


def test_unknown_delivery_blocks_same_request_from_second_ledger_instance(tmp_path):
    path = str(tmp_path / "transport.db")
    first_store = TransportLedger(path)
    second_store = TransportLedger(path)
    first = intent("attempt-a")
    first_store.register_intent(first)
    first_store.commit_observation(
        intent=first,
        observation=observation(first, TransportState.UNKNOWN_DELIVERY),
    )

    with pytest.raises(ValueError, match="unresolved transport attempt"):
        second_store.register_intent(intent("attempt-b"))


def test_different_request_is_not_blocked_by_unknown_delivery(tmp_path):
    store = ledger(tmp_path)
    first = intent("attempt-a")
    store.register_intent(first)
    store.commit_observation(
        intent=first,
        observation=observation(first, TransportState.UNKNOWN_DELIVERY),
    )

    second = intent("attempt-b", request_sha256=digest("different-request"))
    assert store.register_intent(second).created is True


def test_different_provider_is_distinct_transport_subject(tmp_path):
    store = ledger(tmp_path)
    first = intent("attempt-a", provider="ollama")
    store.register_intent(first)
    store.commit_observation(
        intent=first,
        observation=observation(first, TransportState.UNKNOWN_DELIVERY),
    )

    second = intent("attempt-b", provider="lmstudio")
    assert store.register_intent(second).created is True


def test_observation_requires_registered_exact_intent(tmp_path):
    store = ledger(tmp_path)
    i = intent("attempt-a")
    with pytest.raises(ValueError, match="not registered"):
        store.commit_observation(
            intent=i,
            observation=observation(i, TransportState.NOT_SENT),
        )


def test_observation_commit_and_readback_are_exact(tmp_path):
    store = ledger(tmp_path)
    i = intent("attempt-a")
    store.register_intent(i)
    committed = store.commit_observation(
        intent=i,
        observation=observation(
            i,
            TransportState.CONFIRMED_HTTP_RESPONSE,
            status=200,
            response="ok",
        ),
    )
    assert committed.created is True
    assert store.latest_receipt(i.attempt_id) == committed.receipt
    assert committed.receipt.retry_posture is RetryPosture.NO_AUTOMATIC_RETRY


def test_duplicate_identical_observation_is_idempotent(tmp_path):
    store = ledger(tmp_path)
    i = intent("attempt-a")
    store.register_intent(i)
    obs = observation(i, TransportState.NOT_SENT)
    first = store.commit_observation(intent=i, observation=obs)
    second = store.commit_observation(intent=i, observation=obs)
    assert first.created is True
    assert second.created is False
    assert first.sequence == second.sequence
    assert first.receipt == second.receipt


def test_unknown_can_be_reconciled_by_append_only_final_observation(tmp_path):
    store = ledger(tmp_path)
    i = intent("attempt-a")
    store.register_intent(i)
    unknown = store.commit_observation(
        intent=i,
        observation=observation(i, TransportState.UNKNOWN_DELIVERY),
    )
    final = store.commit_observation(
        intent=i,
        observation=observation(
            i,
            TransportState.CONFIRMED_HTTP_RESPONSE,
            status=200,
            response="later-readback",
        ),
    )
    assert final.sequence > unknown.sequence
    history = store.observation_history(i.attempt_id)
    assert [item.state for item in history] == [
        TransportState.UNKNOWN_DELIVERY,
        TransportState.CONFIRMED_HTTP_RESPONSE,
    ]
    assert store.latest_receipt(i.attempt_id) == final.receipt


def test_resolved_unknown_releases_single_flight_registration(tmp_path):
    store = ledger(tmp_path)
    first = intent("attempt-a")
    store.register_intent(first)
    store.commit_observation(
        intent=first,
        observation=observation(first, TransportState.UNKNOWN_DELIVERY),
    )
    store.commit_observation(
        intent=first,
        observation=observation(first, TransportState.NOT_SENT),
    )

    second = intent("attempt-b")
    assert store.register_intent(second).created is True


def test_final_state_cannot_be_rewritten(tmp_path):
    store = ledger(tmp_path)
    i = intent("attempt-a")
    store.register_intent(i)
    store.commit_observation(
        intent=i,
        observation=observation(i, TransportState.NOT_SENT),
    )
    with pytest.raises(ValueError, match="final transport state"):
        store.commit_observation(
            intent=i,
            observation=observation(i, TransportState.UNKNOWN_DELIVERY),
        )


def test_cross_instance_attempt_id_collision_is_fail_closed(tmp_path):
    path = str(tmp_path / "transport.db")
    a = TransportLedger(path)
    b = TransportLedger(path)
    original = intent("attempt-a")
    a.register_intent(original)
    divergent = replace(original, plan_digest=digest("other-plan"))
    with pytest.raises(ValueError, match="diverges"):
        b.register_intent(divergent)


def test_history_is_empty_for_registered_unobserved_attempt(tmp_path):
    store = ledger(tmp_path)
    i = intent("attempt-a")
    store.register_intent(i)
    assert store.latest_receipt(i.attempt_id) is None
    assert store.observation_history(i.attempt_id) == ()
