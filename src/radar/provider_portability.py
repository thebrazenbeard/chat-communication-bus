"""Provider-neutral execution portability primitives.

This module does not call model providers.  It defines deterministic contracts
for deciding whether a provider can accept a governed execution request and for
recording what an adapter claims it submitted/received.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import json
from typing import Iterable


class Capability(StrEnum):
    SYSTEM_INSTRUCTIONS = "SYSTEM_INSTRUCTIONS"
    MULTI_TURN_CONTEXT = "MULTI_TURN_CONTEXT"
    TOOL_CALLS = "TOOL_CALLS"
    STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"
    FILE_INPUT = "FILE_INPUT"
    IMAGE_INPUT = "IMAGE_INPUT"
    LONG_CONTEXT = "LONG_CONTEXT"
    STREAMING = "STREAMING"


class QualificationState(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    DEGRADED = "DEGRADED"
    INELIGIBLE = "INELIGIBLE"


def _nonempty(value: str, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{label} must be a non-empty exact string")
    return value


def _digest_payload(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _require_sha256(value: str, label: str) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or any(ch not in "0123456789abcdef" for ch in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return value


@dataclass(frozen=True, order=True)
class StateReference:
    repository: str
    ref: str
    commit_sha: str
    path: str
    git_blob: str

    def __post_init__(self) -> None:
        _nonempty(self.repository, "repository")
        _nonempty(self.ref, "ref")
        _nonempty(self.path, "path")
        for value, label in (
            (self.commit_sha, "commit_sha"),
            (self.git_blob, "git_blob"),
        ):
            if (
                type(value) is not str
                or len(value) != 40
                or any(ch not in "0123456789abcdef" for ch in value)
            ):
                raise ValueError(
                    f"{label} must be a lowercase Git SHA-1 object id"
                )

    def payload(self) -> dict[str, str]:
        return {
            "repository": self.repository,
            "ref": self.ref,
            "commit_sha": self.commit_sha,
            "path": self.path,
            "git_blob": self.git_blob,
        }


@dataclass(frozen=True)
class PortableExecutionEnvelope:
    subject_id: str
    logical_identity: str
    instruction_sha256: str
    input_sha256: str
    state_refs: tuple[StateReference, ...]
    required_capabilities: tuple[Capability, ...]
    preferred_capabilities: tuple[Capability, ...] = ()
    prohibited_effects: tuple[str, ...] = ()
    authority_scope: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _nonempty(self.subject_id, "subject_id")
        _nonempty(self.logical_identity, "logical_identity")
        _require_sha256(self.instruction_sha256, "instruction_sha256")
        _require_sha256(self.input_sha256, "input_sha256")
        if type(self.state_refs) is not tuple:
            raise ValueError("state_refs must be a tuple")
        if any(type(item) is not StateReference for item in self.state_refs):
            raise ValueError("state_refs must contain exact StateReference values")
        if len(self.state_refs) != len(set(self.state_refs)):
            raise ValueError("state_refs must be unique")
        for values, label in (
            (self.required_capabilities, "required_capabilities"),
            (self.preferred_capabilities, "preferred_capabilities"),
        ):
            if type(values) is not tuple:
                raise ValueError(f"{label} must be a tuple")
            if any(type(item) is not Capability for item in values):
                raise ValueError(f"{label} must contain exact Capability values")
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")
        overlap = set(self.required_capabilities) & set(self.preferred_capabilities)
        if overlap:
            raise ValueError("capabilities cannot be both required and preferred")
        for values, label in (
            (self.prohibited_effects, "prohibited_effects"),
            (self.authority_scope, "authority_scope"),
        ):
            if type(values) is not tuple:
                raise ValueError(f"{label} must be a tuple")
            if any(type(item) is not str or not item.strip() for item in values):
                raise ValueError(f"{label} must contain non-empty exact strings")
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")

    def payload(self) -> dict[str, object]:
        return {
            "schema": "VERA_PORTABLE_EXECUTION_ENVELOPE_V1",
            "subject_id": self.subject_id,
            "logical_identity": self.logical_identity,
            "instruction_sha256": self.instruction_sha256,
            "input_sha256": self.input_sha256,
            "state_refs": [item.payload() for item in sorted(self.state_refs)],
            "required_capabilities": sorted(
                item.value for item in self.required_capabilities
            ),
            "preferred_capabilities": sorted(
                item.value for item in self.preferred_capabilities
            ),
            "prohibited_effects": sorted(self.prohibited_effects),
            "authority_scope": sorted(self.authority_scope),
        }

    @property
    def digest(self) -> str:
        return _digest_payload(self.payload())


@dataclass(frozen=True)
class ProviderManifest:
    provider_id: str
    model_id: str
    adapter_version: str
    capabilities: tuple[Capability, ...]
    max_context_tokens: int | None = None

    def __post_init__(self) -> None:
        _nonempty(self.provider_id, "provider_id")
        _nonempty(self.model_id, "model_id")
        _nonempty(self.adapter_version, "adapter_version")
        if type(self.capabilities) is not tuple:
            raise ValueError("capabilities must be a tuple")
        if any(type(item) is not Capability for item in self.capabilities):
            raise ValueError("capabilities must contain exact Capability values")
        if len(self.capabilities) != len(set(self.capabilities)):
            raise ValueError("capabilities must be unique")
        if self.max_context_tokens is not None:
            if type(self.max_context_tokens) is not int or self.max_context_tokens <= 0:
                raise ValueError("max_context_tokens must be None or positive int")

    def payload(self) -> dict[str, object]:
        return {
            "schema": "VERA_PROVIDER_MANIFEST_V1",
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "adapter_version": self.adapter_version,
            "capabilities": sorted(item.value for item in self.capabilities),
            "max_context_tokens": self.max_context_tokens,
        }

    @property
    def digest(self) -> str:
        return _digest_payload(self.payload())


@dataclass(frozen=True)
class ProviderQualification:
    state: QualificationState
    missing_required: tuple[Capability, ...]
    missing_preferred: tuple[Capability, ...]
    envelope_digest: str
    manifest_digest: str


def qualify_provider(
    envelope: PortableExecutionEnvelope,
    manifest: ProviderManifest,
) -> ProviderQualification:
    if type(envelope) is not PortableExecutionEnvelope:
        raise ValueError("envelope must be exact PortableExecutionEnvelope")
    if type(manifest) is not ProviderManifest:
        raise ValueError("manifest must be exact ProviderManifest")

    available = set(manifest.capabilities)
    missing_required = tuple(
        sorted(
            set(envelope.required_capabilities) - available,
            key=lambda item: item.value,
        )
    )
    missing_preferred = tuple(
        sorted(
            set(envelope.preferred_capabilities) - available,
            key=lambda item: item.value,
        )
    )

    if missing_required:
        state = QualificationState.INELIGIBLE
    elif missing_preferred:
        state = QualificationState.DEGRADED
    else:
        state = QualificationState.ELIGIBLE

    return ProviderQualification(
        state=state,
        missing_required=missing_required,
        missing_preferred=missing_preferred,
        envelope_digest=envelope.digest,
        manifest_digest=manifest.digest,
    )


@dataclass(frozen=True)
class ProviderExecutionReceipt:
    envelope_digest: str
    manifest_digest: str
    provider_id: str
    model_id: str
    adapter_version: str
    consumed_instruction_sha256: str
    consumed_state_blobs: tuple[str, ...]
    output_sha256: str
    adapter_claim: str = "ADAPTER_SUBMISSION_AND_OUTPUT_RECEIPT_ONLY"

    def __post_init__(self) -> None:
        _require_sha256(self.envelope_digest, "envelope_digest")
        _require_sha256(self.manifest_digest, "manifest_digest")
        _nonempty(self.provider_id, "provider_id")
        _nonempty(self.model_id, "model_id")
        _nonempty(self.adapter_version, "adapter_version")
        _require_sha256(
            self.consumed_instruction_sha256, "consumed_instruction_sha256"
        )
        if type(self.consumed_state_blobs) is not tuple:
            raise ValueError("consumed_state_blobs must be a tuple")
        for blob in self.consumed_state_blobs:
            if (
                type(blob) is not str
                or len(blob) != 40
                or any(ch not in "0123456789abcdef" for ch in blob)
            ):
                raise ValueError(
                    "consumed_state_blobs must contain lowercase Git SHA-1 ids"
                )
        if len(self.consumed_state_blobs) != len(set(self.consumed_state_blobs)):
            raise ValueError("consumed_state_blobs must be unique")
        _require_sha256(self.output_sha256, "output_sha256")
        if self.adapter_claim != "ADAPTER_SUBMISSION_AND_OUTPUT_RECEIPT_ONLY":
            raise ValueError("unsupported adapter claim")

    def payload(self) -> dict[str, object]:
        return {
            "schema": "VERA_PROVIDER_EXECUTION_RECEIPT_V1",
            "envelope_digest": self.envelope_digest,
            "manifest_digest": self.manifest_digest,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "adapter_version": self.adapter_version,
            "consumed_instruction_sha256": self.consumed_instruction_sha256,
            "consumed_state_blobs": sorted(self.consumed_state_blobs),
            "output_sha256": self.output_sha256,
            "adapter_claim": self.adapter_claim,
        }

    @property
    def digest(self) -> str:
        return _digest_payload(self.payload())


def verify_execution_receipt(
    envelope: PortableExecutionEnvelope,
    manifest: ProviderManifest,
    receipt: ProviderExecutionReceipt,
) -> None:
    if type(receipt) is not ProviderExecutionReceipt:
        raise ValueError("receipt must be exact ProviderExecutionReceipt")
    qualification = qualify_provider(envelope, manifest)
    if qualification.state is QualificationState.INELIGIBLE:
        raise ValueError("provider is ineligible for this execution envelope")
    if receipt.envelope_digest != envelope.digest:
        raise ValueError("receipt envelope digest mismatch")
    if receipt.manifest_digest != manifest.digest:
        raise ValueError("receipt manifest digest mismatch")
    if (
        receipt.provider_id != manifest.provider_id
        or receipt.model_id != manifest.model_id
        or receipt.adapter_version != manifest.adapter_version
    ):
        raise ValueError("receipt provider/model/adapter mismatch")
    if receipt.consumed_instruction_sha256 != envelope.instruction_sha256:
        raise ValueError("receipt instruction digest mismatch")
    expected_blobs = tuple(sorted(item.git_blob for item in envelope.state_refs))
    if tuple(sorted(receipt.consumed_state_blobs)) != expected_blobs:
        raise ValueError("receipt state blob coverage mismatch")


__all__ = [
    "Capability",
    "PortableExecutionEnvelope",
    "ProviderExecutionReceipt",
    "ProviderManifest",
    "ProviderQualification",
    "QualificationState",
    "StateReference",
    "qualify_provider",
    "verify_execution_receipt",
]
