from dataclasses import replace
from hashlib import sha1, sha256
import json
from urllib.parse import parse_qs, unquote, urlparse

import pytest

import radar.provider_git_provenance as provenance
from radar.provider_execution_binding import prepare_adapter_execution
from radar.provider_git_provenance import GitHubCommitPathResolver
from radar.provider_openai_compatible import (
    LocalOpenAICompatibleProfile,
    LocalOpenAICompatibleRequest,
    build_local_openai_compatible_request,
)
from radar.provider_portability import (
    Capability,
    PortableExecutionEnvelope,
    ProviderManifest,
    StateReference,
)
from radar.provider_routing import (
    ProviderRouteKey,
    ProviderRoutePolicy,
    select_provider_route,
)


INSTRUCTIONS = "Governed system instructions."
TASK = b"Do the task."
STATE = b"reference state\n"


def git_blob(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


def envelope() -> PortableExecutionEnvelope:
    return PortableExecutionEnvelope(
        subject_id="local-adapter-test",
        logical_identity="vera",
        instruction_sha256=sha256(INSTRUCTIONS.encode()).hexdigest(),
        input_sha256=sha256(TASK).hexdigest(),
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
        preferred_capabilities=(),
        prohibited_effects=("MERGE",),
        authority_scope=("READ_GITHUB",),
    )


def manifest(provider: str) -> ProviderManifest:
    return ProviderManifest(
        provider_id=provider,
        model_id="local-model",
        adapter_version="openai-compatible-chat-v1",
        capabilities=(
            Capability.SYSTEM_INSTRUCTIONS,
            Capability.MULTI_TURN_CONTEXT,
        ),
    )


def resolver(monkeypatch) -> GitHubCommitPathResolver:
    ref = envelope().state_refs[0]

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


def prepared(monkeypatch, provider="ollama", task=TASK, state=STATE):
    e = envelope()
    if task != TASK:
        e = PortableExecutionEnvelope(
            subject_id=e.subject_id,
            logical_identity=e.logical_identity,
            instruction_sha256=e.instruction_sha256,
            input_sha256=sha256(task).hexdigest(),
            state_refs=e.state_refs,
            required_capabilities=e.required_capabilities,
            preferred_capabilities=e.preferred_capabilities,
            prohibited_effects=e.prohibited_effects,
            authority_scope=e.authority_scope,
        )
    m = manifest(provider)
    policy = ProviderRoutePolicy(
        policy_id="local-route",
        ordered_routes=(ProviderRouteKey.from_manifest(m),),
    )
    decision = select_provider_route(
        envelope=e,
        manifests=(m,),
        policy=policy,
    )
    return prepare_adapter_execution(
        envelope=e,
        manifest=m,
        decision=decision,
        instruction_text=INSTRUCTIONS,
        input_bytes=task,
        state_blobs={e.state_refs[0].git_blob: state},
        provenance_resolver=resolver(monkeypatch),
    )


@pytest.mark.parametrize(
    ("provider", "base_url", "expected"),
    [
        ("ollama", "http://127.0.0.1:11434", "http://127.0.0.1:11434/v1/chat/completions"),
        ("lmstudio", "http://localhost:1234", "http://localhost:1234/v1/chat/completions"),
    ],
)
def test_builds_loopback_openai_compatible_chat_request(
    monkeypatch, provider, base_url, expected
):
    p = prepared(monkeypatch, provider=provider)
    profile = LocalOpenAICompatibleProfile(
        provider_id=provider,
        adapter_version="openai-compatible-chat-v1",
        base_url=base_url,
    )
    request = build_local_openai_compatible_request(
        prepared=p,
        profile=profile,
    )
    assert request.request_url == expected
    assert request.payload["model"] == "local-model"
    assert request.payload["stream"] is False


def test_system_instructions_remain_system_and_state_remains_reference_context(monkeypatch):
    p = prepared(monkeypatch)
    profile = LocalOpenAICompatibleProfile(
        provider_id="ollama",
        adapter_version="openai-compatible-chat-v1",
        base_url="http://localhost:11434",
    )
    request = build_local_openai_compatible_request(prepared=p, profile=profile)
    messages = request.payload["messages"]
    assert messages[0] == {"role": "system", "content": INSTRUCTIONS}
    assert messages[1]["role"] == "user"
    assert "REFERENCE_CONTEXT_NOT_SYSTEM_AUTHORITY" in messages[1]["content"]
    assert "reference state" in messages[1]["content"]
    assert "Do the task." in messages[1]["content"]


@pytest.mark.parametrize(
    "base_url",
    [
        "https://example.com:443",
        "http://192.168.1.5:11434",
        "http://user:pass@localhost:11434",
        "http://localhost:11434/v1",
        "http://localhost:11434?x=1",
        "ftp://localhost:11434",
        "http://localhost",
    ],
)
def test_profile_rejects_non_loopback_or_ambiguous_endpoint(base_url):
    with pytest.raises(ValueError):
        LocalOpenAICompatibleProfile(
            provider_id="ollama",
            adapter_version="openai-compatible-chat-v1",
            base_url=base_url,
        )


def test_profile_provider_and_adapter_must_match_selected_plan(monkeypatch):
    p = prepared(monkeypatch)
    wrong_provider = LocalOpenAICompatibleProfile(
        provider_id="lmstudio",
        adapter_version="openai-compatible-chat-v1",
        base_url="http://localhost:1234",
    )
    with pytest.raises(ValueError, match="provider mismatch"):
        build_local_openai_compatible_request(
            prepared=p,
            profile=wrong_provider,
        )

    wrong_adapter = LocalOpenAICompatibleProfile(
        provider_id="ollama",
        adapter_version="different-adapter",
        base_url="http://localhost:11434",
    )
    with pytest.raises(ValueError, match="adapter mismatch"):
        build_local_openai_compatible_request(
            prepared=p,
            profile=wrong_adapter,
        )


def test_non_utf8_task_input_fails_closed(monkeypatch):
    raw = b"\xff\xfe"
    p = prepared(monkeypatch, task=raw)
    profile = LocalOpenAICompatibleProfile(
        provider_id="ollama",
        adapter_version="openai-compatible-chat-v1",
        base_url="http://localhost:11434",
    )
    with pytest.raises(ValueError, match="task input is not UTF-8"):
        build_local_openai_compatible_request(
            prepared=p,
            profile=profile,
        )


def test_request_digest_is_deterministic(monkeypatch):
    p = prepared(monkeypatch)
    profile = LocalOpenAICompatibleProfile(
        provider_id="ollama",
        adapter_version="openai-compatible-chat-v1",
        base_url="http://127.0.0.1:11434",
    )
    a = build_local_openai_compatible_request(prepared=p, profile=profile)
    b = build_local_openai_compatible_request(prepared=p, profile=profile)
    assert a.payload_sha256 == b.payload_sha256
    assert a.payload == b.payload
    assert a.request_claim == "LOCAL_LOOPBACK_REQUEST_CONSTRUCTION_ONLY"


def test_request_payload_is_immutable_by_value_and_revalidated(monkeypatch):
    p = prepared(monkeypatch)
    profile = LocalOpenAICompatibleProfile(
        provider_id="ollama",
        adapter_version="openai-compatible-chat-v1",
        base_url="http://127.0.0.1:11434",
    )
    request = build_local_openai_compatible_request(prepared=p, profile=profile)

    detached = request.payload
    detached["model"] = "mutated"
    assert request.payload["model"] == "local-model"

    with pytest.raises(ValueError, match="loopback"):
        replace(
            request,
            request_url="https://example.com:443/v1/chat/completions",
        )

    forged = request.payload
    forged["model"] = "other-model"
    forged_json = json.dumps(
        forged,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    with pytest.raises(ValueError, match="payload model mismatch"):
        replace(
            request,
            payload_json=forged_json,
            payload_sha256=sha256(forged_json.encode("utf-8")).hexdigest(),
        )
