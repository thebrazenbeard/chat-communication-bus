"""Materialize a portable execution envelope from exact bytes.

This module performs no provider/network I/O. It proves only that the bytes handed
to an adapter match the digests and Git objects named by the portable envelope.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1, sha256
from typing import Mapping

from .provider_portability import (
    PortableExecutionEnvelope,
    ProviderManifest,
    QualificationState,
    qualify_provider,
)


def git_blob_sha1(data: bytes) -> str:
    if type(data) is not bytes:
        raise ValueError("git blob material must be exact bytes")
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


@dataclass(frozen=True)
class MaterializedStateObject:
    repository: str
    commit_sha: str
    path: str
    git_blob: str
    content: bytes


@dataclass(frozen=True)
class MaterializedExecutionRequest:
    envelope_digest: str
    manifest_digest: str
    provider_id: str
    model_id: str
    adapter_version: str
    instruction_text: str
    input_bytes: bytes
    state_objects: tuple[MaterializedStateObject, ...]
    qualification: QualificationState


def materialize_execution_request(
    *,
    envelope: PortableExecutionEnvelope,
    manifest: ProviderManifest,
    instruction_text: str,
    input_bytes: bytes,
    state_blobs: Mapping[str, bytes],
) -> MaterializedExecutionRequest:
    if type(envelope) is not PortableExecutionEnvelope:
        raise ValueError("envelope must be exact PortableExecutionEnvelope")
    if type(manifest) is not ProviderManifest:
        raise ValueError("manifest must be exact ProviderManifest")
    if type(instruction_text) is not str:
        raise ValueError("instruction_text must be exact str")
    if type(input_bytes) is not bytes:
        raise ValueError("input_bytes must be exact bytes")
    if not isinstance(state_blobs, Mapping):
        raise ValueError("state_blobs must be a mapping of blob id to bytes")

    qualification = qualify_provider(envelope, manifest)
    if qualification.state is QualificationState.INELIGIBLE:
        raise ValueError("provider is ineligible for this execution envelope")

    instruction_digest = sha256(instruction_text.encode("utf-8")).hexdigest()
    if instruction_digest != envelope.instruction_sha256:
        raise ValueError("instruction material does not match envelope digest")

    input_digest = sha256(input_bytes).hexdigest()
    if input_digest != envelope.input_sha256:
        raise ValueError("input material does not match envelope digest")

    expected_blob_ids = {item.git_blob for item in envelope.state_refs}
    supplied_blob_ids = set(state_blobs)
    missing = expected_blob_ids - supplied_blob_ids
    extra = supplied_blob_ids - expected_blob_ids
    if missing:
        raise ValueError(f"missing state blob material: {sorted(missing)}")
    if extra:
        raise ValueError(f"unexpected state blob material: {sorted(extra)}")

    objects: list[MaterializedStateObject] = []
    for ref in sorted(envelope.state_refs):
        data = state_blobs[ref.git_blob]
        if type(data) is not bytes:
            raise ValueError(f"state blob {ref.git_blob} material must be exact bytes")
        observed = git_blob_sha1(data)
        if observed != ref.git_blob:
            raise ValueError(
                f"state blob content mismatch for {ref.repository}:{ref.path}"
            )
        objects.append(
            MaterializedStateObject(
                repository=ref.repository,
                commit_sha=ref.commit_sha,
                path=ref.path,
                git_blob=ref.git_blob,
                content=data,
            )
        )

    return MaterializedExecutionRequest(
        envelope_digest=envelope.digest,
        manifest_digest=manifest.digest,
        provider_id=manifest.provider_id,
        model_id=manifest.model_id,
        adapter_version=manifest.adapter_version,
        instruction_text=instruction_text,
        input_bytes=input_bytes,
        state_objects=tuple(objects),
        qualification=qualification.state,
    )


__all__ = [
    "MaterializedExecutionRequest",
    "MaterializedStateObject",
    "git_blob_sha1",
    "materialize_execution_request",
]
