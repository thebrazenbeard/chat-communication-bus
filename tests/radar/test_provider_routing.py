from dataclasses import replace
from hashlib import sha256

import pytest

from radar.provider_portability import (
    Capability,
    PortableExecutionEnvelope,
    ProviderManifest,
    StateReference,
)
from radar.provider_routing import (
    ProviderRouteKey,
    ProviderRoutePolicy,
    RouteSelectionState,
    select_provider_route,
)


def envelope() -> PortableExecutionEnvelope:
    return PortableExecutionEnvelope(
        subject_id="route-test",
        logical_identity="vera",
        instruction_sha256=sha256(b"instructions").hexdigest(),
        input_sha256=sha256(b"input").hexdigest(),
        state_refs=(
            StateReference(
                repository="owner/repo",
                repository_id=1001,
                ref="main",
                commit_sha="1" * 40,
                path="state.md",
                git_blob="2" * 40,
            ),
        ),
        required_capabilities=(
            Capability.SYSTEM_INSTRUCTIONS,
            Capability.MULTI_TURN_CONTEXT,
        ),
        preferred_capabilities=(Capability.TOOL_CALLS,),
    )


def manifest(
    provider: str,
    model: str,
    adapter: str,
    *caps: Capability,
) -> ProviderManifest:
    return ProviderManifest(
        provider_id=provider,
        model_id=model,
        adapter_version=adapter,
        capabilities=tuple(caps),
    )


def key(m: ProviderManifest) -> ProviderRouteKey:
    return ProviderRouteKey.from_manifest(m)


def test_policy_order_selects_first_fully_eligible_route():
    e = envelope()
    a = manifest(
        "provider-a",
        "model-a",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
        Capability.TOOL_CALLS,
    )
    b = manifest(
        "provider-b",
        "model-b",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
        Capability.TOOL_CALLS,
    )
    policy = ProviderRoutePolicy(
        policy_id="explicit-order",
        ordered_routes=(key(b), key(a)),
    )
    decision = select_provider_route(
        envelope=e,
        manifests=(a, b),
        policy=policy,
    )
    assert decision.state is RouteSelectionState.SELECTED_ELIGIBLE
    assert decision.route == key(b)
    assert decision.manifest_digest == b.digest


def test_unlisted_provider_is_never_auto_selected_even_if_more_capable():
    e = envelope()
    listed = manifest(
        "listed",
        "model",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
    )
    unlisted = manifest(
        "local-unrestricted",
        "model",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
        Capability.TOOL_CALLS,
        Capability.STRUCTURED_OUTPUT,
    )
    policy = ProviderRoutePolicy(
        policy_id="only-listed",
        ordered_routes=(key(listed),),
        allow_degraded=True,
    )
    decision = select_provider_route(
        envelope=e,
        manifests=(listed, unlisted),
        policy=policy,
    )
    assert decision.state is RouteSelectionState.NO_ROUTE


def test_eligible_route_beats_earlier_degraded_route():
    e = envelope()
    degraded = manifest(
        "preferred-but-degraded",
        "model",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
    )
    eligible = manifest(
        "fully-eligible",
        "model",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
        Capability.TOOL_CALLS,
    )
    policy = ProviderRoutePolicy(
        policy_id="prefer-capability-completeness",
        ordered_routes=(key(degraded), key(eligible)),
        allow_degraded=True,
    )
    decision = select_provider_route(
        envelope=e,
        manifests=(degraded, eligible),
        policy=policy,
    )
    assert decision.state is RouteSelectionState.SELECTED_ELIGIBLE
    assert decision.route == key(eligible)


def test_degraded_route_requires_explicit_policy_permission():
    e = envelope()
    degraded = manifest(
        "provider",
        "model",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
    )

    denied = ProviderRoutePolicy(
        policy_id="no-degraded",
        ordered_routes=(key(degraded),),
        allow_degraded=False,
    )
    assert (
        select_provider_route(
            envelope=e,
            manifests=(degraded,),
            policy=denied,
        ).state
        is RouteSelectionState.NO_ROUTE
    )

    allowed = ProviderRoutePolicy(
        policy_id="explicit-degraded",
        ordered_routes=(key(degraded),),
        allow_degraded=True,
    )
    assert (
        select_provider_route(
            envelope=e,
            manifests=(degraded,),
            policy=allowed,
        ).state
        is RouteSelectionState.SELECTED_DEGRADED
    )


def test_required_capability_gap_never_becomes_degraded_route():
    e = envelope()
    missing_required = manifest(
        "provider",
        "model",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.TOOL_CALLS,
    )
    policy = ProviderRoutePolicy(
        policy_id="allow-degraded",
        ordered_routes=(key(missing_required),),
        allow_degraded=True,
    )
    decision = select_provider_route(
        envelope=e,
        manifests=(missing_required,),
        policy=policy,
    )
    assert decision.state is RouteSelectionState.NO_ROUTE


def test_exact_model_and_adapter_binding_prevents_provider_id_substitution():
    e = envelope()
    approved = ProviderRouteKey("provider", "approved-model", "adapter-v1")
    substitute = manifest(
        "provider",
        "other-model",
        "adapter-v2",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
        Capability.TOOL_CALLS,
    )
    policy = ProviderRoutePolicy(
        policy_id="exact-route",
        ordered_routes=(approved,),
    )
    decision = select_provider_route(
        envelope=e,
        manifests=(substitute,),
        policy=policy,
    )
    assert decision.state is RouteSelectionState.NO_ROUTE


def test_duplicate_manifest_for_same_exact_route_fails_closed():
    e = envelope()
    a = manifest(
        "provider",
        "model",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
    )
    b = manifest(
        "provider",
        "model",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
        Capability.TOOL_CALLS,
    )
    policy = ProviderRoutePolicy(
        policy_id="duplicates",
        ordered_routes=(key(a),),
        allow_degraded=True,
    )
    with pytest.raises(ValueError, match="duplicate provider route manifest"):
        select_provider_route(
            envelope=e,
            manifests=(a, b),
            policy=policy,
        )


def test_duplicate_policy_route_fails_closed():
    route = ProviderRouteKey("provider", "model", "v1")
    with pytest.raises(ValueError, match="ordered_routes must be unique"):
        ProviderRoutePolicy(
            policy_id="bad",
            ordered_routes=(route, route),
        )


def test_route_decision_explicitly_grants_no_effect_authority():
    e = envelope()
    m = manifest(
        "provider",
        "model",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
        Capability.TOOL_CALLS,
    )
    policy = ProviderRoutePolicy(
        policy_id="authority-separation",
        ordered_routes=(key(m),),
    )
    decision = select_provider_route(
        envelope=e,
        manifests=(m,),
        policy=policy,
    )
    assert decision.decision_claim == "ROUTE_SELECTION_ONLY_NO_EFFECT_AUTHORITY"


def test_allow_degraded_must_be_actual_bool():
    route = ProviderRouteKey("provider", "model", "v1")
    with pytest.raises(ValueError, match="allow_degraded"):
        ProviderRoutePolicy(
            policy_id="bad",
            ordered_routes=(route,),
            allow_degraded=1,
        )


def test_policy_object_does_not_claim_user_or_effect_authority():
    route = ProviderRouteKey("provider", "model", "v1")
    policy = ProviderRoutePolicy(
        policy_id="bounded-policy",
        ordered_routes=(route,),
    )
    assert policy.policy_claim == "ROUTE_PREFERENCE_INPUT_ONLY_NOT_AUTHORITY"
    with pytest.raises(ValueError, match="unsupported route policy claim"):
        ProviderRoutePolicy(
            policy_id="forged-authority",
            ordered_routes=(route,),
            policy_claim="PATRICK_AUTHORIZED",
        )


def test_selected_decision_rejects_qualification_state_or_digest_rebinding():
    e = envelope()
    m = manifest(
        "provider",
        "model",
        "v1",
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
        Capability.TOOL_CALLS,
    )
    policy = ProviderRoutePolicy(
        policy_id="self-consistency",
        ordered_routes=(key(m),),
    )
    decision = select_provider_route(
        envelope=e,
        manifests=(m,),
        policy=policy,
    )
    with pytest.raises(ValueError, match="qualification state mismatch"):
        replace(
            decision,
            state=RouteSelectionState.SELECTED_DEGRADED,
        )
    with pytest.raises(ValueError, match="manifest/qualification mismatch"):
        replace(
            decision,
            manifest_digest="f" * 64,
        )
