from hashlib import sha1, sha256

import pytest

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
                repository="repo/a",
                ref="main",
                commit_sha="1" * 40,
                path="a.md",
                git_blob=git_blob(STATE_A),
            ),
            StateReference(
                repository="repo/b",
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


def test_git_blob_sha_matches_git_object_hash_rule():
    assert git_blob_sha1(STATE_A) == git_blob(STATE_A)


def test_materialization_accepts_exact_instruction_input_and_state_bytes():
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS, Capability.TOOL_CALLS)
    req = materialize_execution_request(
        envelope=e,
        manifest=m,
        instruction_text=INSTRUCTION_TEXT,
        input_bytes=INPUT_BYTES,
        state_blobs={
            e.state_refs[0].git_blob: STATE_A,
            e.state_refs[1].git_blob: STATE_B,
        },
    )
    assert req.envelope_digest == e.digest
    assert req.manifest_digest == m.digest
    assert req.qualification is QualificationState.ELIGIBLE
    assert tuple(item.content for item in req.state_objects) == (STATE_A, STATE_B)


def test_materialization_can_continue_on_degraded_preferred_capability():
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    req = materialize_execution_request(
        envelope=e,
        manifest=m,
        instruction_text=INSTRUCTION_TEXT,
        input_bytes=INPUT_BYTES,
        state_blobs={
            e.state_refs[0].git_blob: STATE_A,
            e.state_refs[1].git_blob: STATE_B,
        },
    )
    assert req.qualification is QualificationState.DEGRADED


def test_materialization_rejects_ineligible_provider():
    e = envelope()
    m = manifest()
    with pytest.raises(ValueError, match="ineligible"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs={
                e.state_refs[0].git_blob: STATE_A,
                e.state_refs[1].git_blob: STATE_B,
            },
        )


def test_instruction_and_input_bytes_must_match_envelope():
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    blobs = {
        e.state_refs[0].git_blob: STATE_A,
        e.state_refs[1].git_blob: STATE_B,
    }
    with pytest.raises(ValueError, match="instruction material"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text="different",
            input_bytes=INPUT_BYTES,
            state_blobs=blobs,
        )
    with pytest.raises(ValueError, match="input material"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=b"different",
            state_blobs=blobs,
        )


def test_state_material_must_match_exact_git_blob():
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
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
        )


def test_missing_or_extra_state_blob_material_fails_closed():
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    with pytest.raises(ValueError, match="missing state blob material"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs={e.state_refs[0].git_blob: STATE_A},
        )
    with pytest.raises(ValueError, match="unexpected state blob material"):
        materialize_execution_request(
            envelope=e,
            manifest=m,
            instruction_text=INSTRUCTION_TEXT,
            input_bytes=INPUT_BYTES,
            state_blobs={
                e.state_refs[0].git_blob: STATE_A,
                e.state_refs[1].git_blob: STATE_B,
                "f" * 40: b"extra",
            },
        )
