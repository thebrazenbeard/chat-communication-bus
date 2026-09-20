from dataclasses import replace
from hashlib import sha1, sha256
from urllib.parse import parse_qs, unquote, urlparse

import pytest

import radar.provider_git_provenance as provenance
from radar.provider_execution_binding import (
    PreparedAdapterExecution,
    prepare_adapter_execution,
)
from radar.provider_git_provenance import GitHubCommitPathResolver
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


INSTRUCTION_TEXT = "governed instructions"
INPUT_BYTES = b"user input"
STATE = b"portable state\n"


def git_blob(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


def envelope() -> PortableExecutionEnvelope:
    return PortableExecutionEnvelope(
        subject_id="adapter-binding-test",
        logical_identity="vera",
        instruction_sha256=sha256(INSTRUCTION_TEXT.encode()).hexdigest(),
        input_sha256=sha256(INPUT_BYTES).hexdigest(),
        state_refs=(
            StateReference(
                repository="owner/repo",
                repository_id=1001,
                ref="main",
                commit_sha="1" * 40,
                path="state.md",
                git_blob=git_blob(STATE),
            ),
        ),
        required_capabilities=(
            Capability.SYSTEM_INSTRUCTIONS,
            Capability.MULTI_TURN_CONTEXT,
        ),
        preferred_capabilities=(Capability.TOOL_CALLS,),
        prohibited_effects=("MERGE", "DEPLOY"),
        authority_scope=("READ_GITHUB",),
    )


def manifest(
    provider="provider",
    model="model",
    adapter="adapter-v1",
    *,
    tool_calls=True,
) -> ProviderManifest:
    caps = [
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
    ]
    if tool_calls:
        caps.append(Capability.TOOL_CALLS)
    return ProviderManifest(
        provider_id=provider,
        model_id=model,
        adapter_version=adapter,
        capabilities=tuple(caps),
    )


def install_readback(monkeypatch) -> GitHubCommitPathResolver:
    e = envelope()
    ref = e.state_refs[0]

    def fake_get(url: str, *, token: str | None, timeout: float):
        parsed = urlparse(url)
        parts = [unquote(part) for part in parsed.path.split("/") if part]
        if parts == ["repos", "owner", "repo"]:
            return {"full_name": ref.repository, "id": ref.repository_id}
        if parts == ["repos", "owner", "repo", "git", "commits", ref.commit_sha]:
            return {"sha": ref.commit_sha}
        if parts == ["repos", "owner", "repo", "contents", "state.md"]:
            assert parse_qs(parsed.query)["ref"] == [ref.commit_sha]
            return {"type": "file", "path": ref.path, "sha": ref.git_blob}
        raise ValueError("GitHub provenance readback failed with HTTP 404")

    monkeypatch.setattr(provenance, "_github_get_json", fake_get)
    return GitHubCommitPathResolver()


def decision_for(e, m, *, allow_degraded=False):
    policy = ProviderRoutePolicy(
        policy_id="route-policy",
        ordered_routes=(ProviderRouteKey.from_manifest(m),),
        allow_degraded=allow_degraded,
    )
    return select_provider_route(
        envelope=e,
        manifests=(m,),
        policy=policy,
    )


def prepare(monkeypatch, e=None, m=None, d=None):
    e = e or envelope()
    m = m or manifest()
    d = d or decision_for(e, m)
    return prepare_adapter_execution(
        envelope=e,
        manifest=m,
        decision=d,
        instruction_text=INSTRUCTION_TEXT,
        input_bytes=INPUT_BYTES,
        state_blobs={e.state_refs[0].git_blob: STATE},
        provenance_resolver=install_readback(monkeypatch),
    )


def test_prepare_binds_exact_route_policy_material_and_effect_limits(monkeypatch):
    e = envelope()
    m = manifest()
    d = decision_for(e, m)
    prepared = prepare(monkeypatch, e, m, d)

    assert prepared.plan.envelope_digest == e.digest
    assert prepared.plan.manifest_digest == m.digest
    assert prepared.plan.policy_digest == d.policy_digest
    assert prepared.plan.provider_id == m.provider_id
    assert prepared.plan.model_id == m.model_id
    assert prepared.plan.adapter_version == m.adapter_version
    assert prepared.plan.prohibited_effects == ("DEPLOY", "MERGE")
    assert prepared.plan.authority_scope == ("READ_GITHUB",)
    assert prepared.plan.plan_claim == (
        "ADAPTER_BINDING_ONLY_NO_PROVIDER_EXECUTION_AUTHORITY"
    )


def test_no_route_cannot_be_laundered_into_execution(monkeypatch):
    e = envelope()
    unqualified = ProviderManifest(
        provider_id="provider",
        model_id="model",
        adapter_version="adapter-v1",
        capabilities=(Capability.SYSTEM_INSTRUCTIONS,),
    )
    d = decision_for(e, unqualified, allow_degraded=True)
    assert d.state is RouteSelectionState.NO_ROUTE
    with pytest.raises(ValueError, match="NO_ROUTE"):
        prepare(monkeypatch, e, unqualified, d)


def test_route_decision_cannot_be_reused_for_another_manifest(monkeypatch):
    e = envelope()
    approved = manifest()
    d = decision_for(e, approved)
    substitute = manifest(provider="other-provider")
    with pytest.raises(ValueError, match="manifest mismatch"):
        prepare(monkeypatch, e, substitute, d)


def test_route_decision_cannot_be_reused_for_another_envelope(monkeypatch):
    e = envelope()
    m = manifest()
    d = decision_for(e, m)
    other = replace(
        e,
        subject_id="different-subject",
        input_sha256=sha256(b"different").hexdigest(),
    )
    with pytest.raises(ValueError, match="envelope mismatch"):
        prepare(monkeypatch, other, m, d)


def test_degraded_route_remains_explicitly_degraded_through_preparation(monkeypatch):
    e = envelope()
    degraded = manifest(tool_calls=False)
    d = decision_for(e, degraded, allow_degraded=True)
    assert d.state is RouteSelectionState.SELECTED_DEGRADED
    prepared = prepare(monkeypatch, e, degraded, d)
    assert prepared.plan.route_state is RouteSelectionState.SELECTED_DEGRADED
    assert prepared.materialized.qualification.value == "DEGRADED"


def test_tampered_state_still_fails_at_execution_preparation(monkeypatch):
    e = envelope()
    m = manifest()
    d = decision_for(e, m)
    with pytest.raises(ValueError, match="state blob content mismatch"):
        prepare_adapter_execution(
            envelope=e,
            manifest=m,
            decision=d,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs={e.state_refs[0].git_blob: b"tampered"},
            provenance_resolver=install_readback(monkeypatch),
        )


def test_prepared_execution_rejects_manual_route_rebinding(monkeypatch):
    prepared = prepare(monkeypatch)
    forged_plan = replace(prepared.plan, provider_id="other-provider")
    with pytest.raises(ValueError, match="route mismatch"):
        PreparedAdapterExecution(
            plan=forged_plan,
            materialized=prepared.materialized,
        )


def test_prepared_execution_rejects_state_coverage_rebinding(monkeypatch):
    prepared = prepare(monkeypatch)
    forged_plan = replace(prepared.plan, state_blobs=("f" * 40,))
    with pytest.raises(ValueError, match="state coverage mismatch"):
        PreparedAdapterExecution(
            plan=forged_plan,
            materialized=prepared.materialized,
        )
