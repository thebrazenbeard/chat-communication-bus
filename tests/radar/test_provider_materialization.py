from dataclasses import replace
from hashlib import sha1, sha256
from urllib.parse import parse_qs, unquote, urlparse

import pytest

import radar.provider_git_provenance as provenance
from radar.provider_git_provenance import GitHubCommitPathResolver
from radar.provider_materialization import (
    git_blob_sha1,
    materialize_execution_request,
)
from radar.provider_portability import (
    Capability,
    PortableExecutionEnvelope,
    ProviderManifest,
    QualificationState,
    StateReference,
)


INSTRUCTION_TEXT = "governed instructions"
INPUT_BYTES = b"user input"
STATE_A = b"state object a\n"
STATE_B = b"state object b\n"


def git_blob(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


def envelope() -> PortableExecutionEnvelope:
    return PortableExecutionEnvelope(
        subject_id="materialization-test",
        logical_identity="vera",
        instruction_sha256=sha256(INSTRUCTION_TEXT.encode("utf-8")).hexdigest(),
        input_sha256=sha256(INPUT_BYTES).hexdigest(),
        state_refs=(
            StateReference(
                repository="owner/repo-a",
                ref="main",
                commit_sha="1" * 40,
                path="a.md",
                git_blob=git_blob(STATE_A),
            ),
            StateReference(
                repository="owner/repo-b",
                ref="state/current",
                commit_sha="2" * 40,
                path="b.json",
                git_blob=git_blob(STATE_B),
            ),
        ),
        required_capabilities=(Capability.SYSTEM_INSTRUCTIONS,),
        preferred_capabilities=(Capability.TOOL_CALLS,),
    )


def manifest(*caps: Capability) -> ProviderManifest:
    return ProviderManifest(
        provider_id="provider",
        model_id="model",
        adapter_version="v1",
        capabilities=tuple(caps),
    )


def install_github_readback(
    monkeypatch: pytest.MonkeyPatch,
    *,
    extra: dict[tuple[str, str, str], str] | None = None,
) -> GitHubCommitPathResolver:
    objects = {
        ("owner/repo-a", "1" * 40, "a.md"): git_blob(STATE_A),
        ("owner/repo-b", "2" * 40, "b.json"): git_blob(STATE_B),
    }
    if extra:
        objects.update(extra)

    def fake_get(url: str, *, token: str | None, timeout: float):
        parsed = urlparse(url)
        parts = [unquote(part) for part in parsed.path.split("/") if part]
        if len(parts) < 5 or parts[0] != "repos":
            raise ValueError("unexpected GitHub API path")
        repository = f"{parts[1]}/{parts[2]}"
        if parts[3:5] == ["git", "commits"]:
            commit_sha = parts[5]
            if any(
                repo == repository and commit == commit_sha
                for repo, commit, _ in objects
            ):
                return {"sha": commit_sha}
            raise ValueError("GitHub provenance readback failed with HTTP 404")
        if parts[3] == "contents":
            path = "/".join(parts[4:])
            commit_sha = parse_qs(parsed.query).get("ref", [""])[0]
            blob = objects.get((repository, commit_sha, path))
            if blob is None:
                raise ValueError("GitHub provenance readback failed with HTTP 404")
            return {"type": "file", "path": path, "sha": blob}
        raise ValueError("unexpected GitHub API path")

    monkeypatch.setattr(provenance, "_github_get_json", fake_get)
    return GitHubCommitPathResolver()


def blobs(e: PortableExecutionEnvelope) -> dict[str, bytes]:
    return {
        e.state_refs[0].git_blob: STATE_A,
        e.state_refs[1].git_blob: STATE_B,
    }


def materialize(
    monkeypatch: pytest.MonkeyPatch,
    e: PortableExecutionEnvelope,
    m: ProviderManifest,
):
    return materialize_execution_request(
        envelope=e,
        manifest=m,
        instruction_text=INSTRUCTION_TEXT,
        input_bytes=INPUT_BYTES,
        state_blobs=blobs(e),
        provenance_resolver=install_github_readback(monkeypatch),
    )


def test_git_blob_sha_matches_git_object_hash_rule():
    assert git_blob_sha1(STATE_A) == git_blob(STATE_A)


def test_materialization_accepts_exact_instruction_input_state_and_git_provenance(
    monkeypatch,
):
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS, Capability.TOOL_CALLS)
    req = materialize(monkeypatch, e, m)
    assert req.envelope_digest == e.digest
    assert req.manifest_digest == m.digest
    assert req.qualification is QualificationState.ELIGIBLE
    assert tuple(item.content for item in req.state_objects) == (STATE_A, STATE_B)
    assert tuple(item.git_blob for item in req.provenance_receipts) == (
        e.state_refs[0].git_blob,
        e.state_refs[1].git_blob,
    )


def test_materialization_can_continue_on_degraded_preferred_capability(monkeypatch):
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    req = materialize(monkeypatch, e, m)
    assert req.qualification is QualificationState.DEGRADED


def test_materialization_rejects_ineligible_provider(monkeypatch):
    e = envelope()
    m = manifest()
    with pytest.raises(ValueError, match="ineligible"):
        materialize(monkeypatch, e, m)


def test_instruction_and_input_bytes_must_match_envelope(monkeypatch):
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    resolver = install_github_readback(monkeypatch)
    with pytest.raises(ValueError, match="instruction material"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text="different",
            input_bytes=INPUT_BYTES,
            state_blobs=blobs(e),
            provenance_resolver=resolver,
        )
    with pytest.raises(ValueError, match="input material"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=b"different",
            state_blobs=blobs(e),
            provenance_resolver=resolver,
        )


def test_state_material_must_match_exact_git_blob(monkeypatch):
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    resolver = install_github_readback(monkeypatch)
    with pytest.raises(ValueError, match="state blob content mismatch"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs={
                e.state_refs[0].git_blob: b"tampered",
                e.state_refs[1].git_blob: STATE_B,
            },
            provenance_resolver=resolver,
        )


def test_missing_or_extra_state_blob_material_fails_closed(monkeypatch):
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    resolver = install_github_readback(monkeypatch)
    with pytest.raises(ValueError, match="missing state blob material"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs={e.state_refs[0].git_blob: STATE_A},
            provenance_resolver=resolver,
        )
    with pytest.raises(ValueError, match="unexpected state blob material"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs={
                **blobs(e),
                "f" * 40: b"extra",
            },
            provenance_resolver=resolver,
        )


def test_fake_repository_with_correct_blob_bytes_is_rejected(monkeypatch):
    e = envelope()
    fake = replace(
        e.state_refs[0],
        repository="definitely/not-a-real-repo",
    )
    attacked = replace(e, state_refs=(fake, e.state_refs[1]))
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    resolver = install_github_readback(monkeypatch)
    with pytest.raises(ValueError, match="readback failed"):
        materialize_execution_request(
            envelope=attacked,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs=blobs(e),
            provenance_resolver=resolver,
        )


def test_fake_commit_with_correct_blob_bytes_is_rejected(monkeypatch):
    e = envelope()
    fake = replace(e.state_refs[0], commit_sha="a" * 40)
    attacked = replace(e, state_refs=(fake, e.state_refs[1]))
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    resolver = install_github_readback(monkeypatch)
    with pytest.raises(ValueError, match="readback failed"):
        materialize_execution_request(
            envelope=attacked,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs=blobs(e),
            provenance_resolver=resolver,
        )


def test_wrong_path_with_correct_blob_bytes_is_rejected(monkeypatch):
    e = envelope()
    fake = replace(e.state_refs[0], path="does/not/exist.txt")
    attacked = replace(e, state_refs=(fake, e.state_refs[1]))
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    resolver = install_github_readback(monkeypatch)
    with pytest.raises(ValueError, match="readback failed"):
        materialize_execution_request(
            envelope=attacked,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs=blobs(e),
            provenance_resolver=resolver,
        )


def test_unrelated_commit_path_cannot_borrow_correct_blob_bytes(monkeypatch):
    e = envelope()
    unrelated_commit = "3" * 40
    unrelated_path = "other.md"
    fake = replace(
        e.state_refs[0],
        commit_sha=unrelated_commit,
        path=unrelated_path,
    )
    attacked = replace(e, state_refs=(fake, e.state_refs[1]))
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    resolver = install_github_readback(
        monkeypatch,
        extra={
            ("owner/repo-a", unrelated_commit, unrelated_path): git_blob(STATE_B)
        },
    )
    with pytest.raises(ValueError, match="commit/path blob mismatch"):
        materialize_execution_request(
            envelope=attacked,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs=blobs(e),
            provenance_resolver=resolver,
        )


def test_unverified_or_substitute_resolver_is_rejected():
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)

    class FakeResolver:
        def resolve(self, reference):
            return reference

    with pytest.raises(ValueError, match="exact GitHubCommitPathResolver"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs=blobs(e),
            provenance_resolver=FakeResolver(),
        )
