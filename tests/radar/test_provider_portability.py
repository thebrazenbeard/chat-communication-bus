from hashlib import sha256

import pytest

from radar.provider_portability import (
    Capability,
    PortableExecutionEnvelope,
    ProviderExecutionReceipt,
    ProviderManifest,
    QualificationState,
    StateReference,
    qualify_provider,
    verify_execution_receipt,
)


INSTRUCTION = sha256(b"instructions").hexdigest()
INPUT = sha256(b"input").hexdigest()
OUTPUT = sha256(b"output").hexdigest()
BLOB_A = "a" * 40
BLOB_B = "b" * 40


def envelope() -> PortableExecutionEnvelope:
    return PortableExecutionEnvelope(
        subject_id="vera-freedom-test",
        logical_identity="vera",
        instruction_sha256=INSTRUCTION,
        input_sha256=INPUT,
        state_refs=(
            StateReference(
                repository="thebrazenbeard/vera-control-plane",
                ref="main",
                path="control/current.json",
                git_blob=BLOB_A,
            ),
            StateReference(
                repository="thebrazenbeard/chat-communication-bus",
                ref="bus/vera-v2",
                path="messages/example.md",
                git_blob=BLOB_B,
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


def manifest(*caps: Capability) -> ProviderManifest:
    return ProviderManifest(
        provider_id="provider-x",
        model_id="model-y",
        adapter_version="adapter-v1",
        capabilities=tuple(caps),
        max_context_tokens=128000,
    )


def receipt(
    e: PortableExecutionEnvelope,
    m: ProviderManifest,
    *,
    blobs=(BLOB_A, BLOB_B),
    instruction=INSTRUCTION,
) -> ProviderExecutionReceipt:
    return ProviderExecutionReceipt(
        envelope_digest=e.digest,
        manifest_digest=m.digest,
        provider_id=m.provider_id,
        model_id=m.model_id,
        adapter_version=m.adapter_version,
        consumed_instruction_sha256=instruction,
        consumed_state_blobs=tuple(blobs),
        output_sha256=OUTPUT,
    )


def test_envelope_digest_is_order_stable_for_set_like_fields():
    first = envelope()
    second = PortableExecutionEnvelope(
        subject_id=first.subject_id,
        logical_identity=first.logical_identity,
        instruction_sha256=first.instruction_sha256,
        input_sha256=first.input_sha256,
        state_refs=tuple(reversed(first.state_refs)),
        required_capabilities=tuple(reversed(first.required_capabilities)),
        preferred_capabilities=first.preferred_capabilities,
        prohibited_effects=tuple(reversed(first.prohibited_effects)),
        authority_scope=first.authority_scope,
    )
    assert first.digest == second.digest


def test_required_capability_gap_is_ineligible():
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    q = qualify_provider(e, m)
    assert q.state is QualificationState.INELIGIBLE
    assert q.missing_required == (Capability.MULTI_TURN_CONTEXT,)


def test_preferred_capability_gap_is_degraded_not_ineligible():
    e = envelope()
    m = manifest(
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
    )
    q = qualify_provider(e, m)
    assert q.state is QualificationState.DEGRADED
    assert q.missing_preferred == (Capability.TOOL_CALLS,)


def test_full_capability_match_is_eligible():
    e = envelope()
    m = manifest(
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
        Capability.TOOL_CALLS,
    )
    assert qualify_provider(e, m).state is QualificationState.ELIGIBLE


def test_receipt_requires_exact_instruction_and_state_coverage():
    e = envelope()
    m = manifest(
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
    )
    verify_execution_receipt(e, m, receipt(e, m))

    with pytest.raises(ValueError, match="instruction digest mismatch"):
        verify_execution_receipt(
            e,
            m,
            receipt(e, m, instruction=sha256(b"other").hexdigest()),
        )

    with pytest.raises(ValueError, match="state blob coverage mismatch"):
        verify_execution_receipt(e, m, receipt(e, m, blobs=(BLOB_A,)))


def test_receipt_cannot_rebind_to_another_provider_manifest():
    e = envelope()
    m = manifest(
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
    )
    other = ProviderManifest(
        provider_id="provider-z",
        model_id="model-y",
        adapter_version="adapter-v1",
        capabilities=m.capabilities,
    )
    with pytest.raises(ValueError, match="manifest digest mismatch"):
        verify_execution_receipt(e, other, receipt(e, m))


def test_ineligible_provider_cannot_produce_accepted_receipt():
    e = envelope()
    m = manifest(Capability.SYSTEM_INSTRUCTIONS)
    r = ProviderExecutionReceipt(
        envelope_digest=e.digest,
        manifest_digest=m.digest,
        provider_id=m.provider_id,
        model_id=m.model_id,
        adapter_version=m.adapter_version,
        consumed_instruction_sha256=e.instruction_sha256,
        consumed_state_blobs=(BLOB_A, BLOB_B),
        output_sha256=OUTPUT,
    )
    with pytest.raises(ValueError, match="ineligible"):
        verify_execution_receipt(e, m, r)


def test_receipt_claim_is_bounded_to_adapter_submission_not_provider_truth():
    e = envelope()
    m = manifest(
        Capability.SYSTEM_INSTRUCTIONS,
        Capability.MULTI_TURN_CONTEXT,
    )
    r = receipt(e, m)
    assert r.adapter_claim == "ADAPTER_SUBMISSION_AND_OUTPUT_RECEIPT_ONLY"
    assert "provider_obeyed" not in r.payload()
    assert "safety_bypassed" not in r.payload()
