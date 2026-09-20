"""Bind a selected provider route to exact verified execution material.

This layer still performs no provider call.  It closes the seam between route
selection and provider-specific submission by reusing the authoritative GitHub
provenance/materialization path and binding the result to the selected exact
provider/model/adapter tuple.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Mapping

from .provider_git_provenance import GitHubCommitPathResolver
from .provider_materialization import (
    MaterializedExecutionRequest,
    materialize_execution_request,
)
from .provider_portability import (
    PortableExecutionEnvelope,
    ProviderManifest,
    QualificationState,
)
from .provider_routing import (
    ProviderRouteDecision,
    ProviderRouteKey,
    RouteSelectionState,
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True)
class AdapterExecutionPlan:
    envelope_digest: str
    manifest_digest: str
    policy_digest: str
    provider_id: str
    model_id: str
    adapter_version: str
    route_state: RouteSelectionState
    instruction_sha256: str
    input_sha256: str
    state_blobs: tuple[str, ...]
    prohibited_effects: tuple[str, ...]
    authority_scope: tuple[str, ...]
    plan_claim: str = "ADAPTER_BINDING_ONLY_NO_PROVIDER_EXECUTION_AUTHORITY"

    def __post_init__(self) -> None:
        if self.plan_claim != "ADAPTER_BINDING_ONLY_NO_PROVIDER_EXECUTION_AUTHORITY":
            raise ValueError("unsupported adapter execution plan claim")
        for value, label in (
            (self.envelope_digest, "envelope_digest"),
            (self.manifest_digest, "manifest_digest"),
            (self.policy_digest, "policy_digest"),
            (self.instruction_sha256, "instruction_sha256"),
            (self.input_sha256, "input_sha256"),
        ):
            if (
                type(value) is not str
                or len(value) != 64
                or any(ch not in "0123456789abcdef" for ch in value)
            ):
                raise ValueError(f"{label} must be lowercase SHA-256")
        for value, label in (
            (self.provider_id, "provider_id"),
            (self.model_id, "model_id"),
            (self.adapter_version, "adapter_version"),
        ):
            if type(value) is not str or not value.strip():
                raise ValueError(f"{label} must be non-empty exact string")
        if self.route_state not in (
            RouteSelectionState.SELECTED_ELIGIBLE,
            RouteSelectionState.SELECTED_DEGRADED,
        ):
            raise ValueError("adapter execution plan requires selected route")
        if type(self.state_blobs) is not tuple or not self.state_blobs:
            raise ValueError("state_blobs must be a non-empty tuple")
        for blob in self.state_blobs:
            if (
                type(blob) is not str
                or len(blob) != 40
                or any(ch not in "0123456789abcdef" for ch in blob)
            ):
                raise ValueError("state_blobs must contain lowercase Git SHA-1 ids")
        if len(self.state_blobs) != len(set(self.state_blobs)):
            raise ValueError("state_blobs must be unique")
        for values, label in (
            (self.prohibited_effects, "prohibited_effects"),
            (self.authority_scope, "authority_scope"),
        ):
            if type(values) is not tuple:
                raise ValueError(f"{label} must be tuple")
            if any(type(item) is not str or not item.strip() for item in values):
                raise ValueError(f"{label} must contain non-empty exact strings")
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")

    def payload(self) -> dict[str, object]:
        return {
            "schema": "VERA_ADAPTER_EXECUTION_PLAN_V1",
            "envelope_digest": self.envelope_digest,
            "manifest_digest": self.manifest_digest,
            "policy_digest": self.policy_digest,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "adapter_version": self.adapter_version,
            "route_state": self.route_state.value,
            "instruction_sha256": self.instruction_sha256,
            "input_sha256": self.input_sha256,
            "state_blobs": sorted(self.state_blobs),
            "prohibited_effects": sorted(self.prohibited_effects),
            "authority_scope": sorted(self.authority_scope),
            "plan_claim": self.plan_claim,
        }

    @property
    def digest(self) -> str:
        return _digest(self.payload())


@dataclass(frozen=True)
class PreparedAdapterExecution:
    plan: AdapterExecutionPlan
    materialized: MaterializedExecutionRequest

    def __post_init__(self) -> None:
        if type(self.plan) is not AdapterExecutionPlan:
            raise ValueError("plan must be exact AdapterExecutionPlan")
        if type(self.materialized) is not MaterializedExecutionRequest:
            raise ValueError("materialized must be exact MaterializedExecutionRequest")
        if self.materialized.envelope_digest != self.plan.envelope_digest:
            raise ValueError("prepared execution envelope mismatch")
        if self.materialized.manifest_digest != self.plan.manifest_digest:
            raise ValueError("prepared execution manifest mismatch")
        if (
            self.materialized.provider_id != self.plan.provider_id
            or self.materialized.model_id != self.plan.model_id
            or self.materialized.adapter_version != self.plan.adapter_version
        ):
            raise ValueError("prepared execution route mismatch")
        if self.materialized.qualification.value not in (
            QualificationState.ELIGIBLE.value,
            QualificationState.DEGRADED.value,
        ):
            raise ValueError("prepared execution qualification is not executable")
        if tuple(sorted(item.git_blob for item in self.materialized.state_objects)) != (
            tuple(sorted(self.plan.state_blobs))
        ):
            raise ValueError("prepared execution state coverage mismatch")


def prepare_adapter_execution(
    *,
    envelope: PortableExecutionEnvelope,
    manifest: ProviderManifest,
    decision: ProviderRouteDecision,
    instruction_text: str,
    input_bytes: bytes,
    state_blobs: Mapping[str, bytes],
    provenance_resolver: GitHubCommitPathResolver,
) -> PreparedAdapterExecution:
    if type(envelope) is not PortableExecutionEnvelope:
        raise ValueError("envelope must be exact PortableExecutionEnvelope")
    if type(manifest) is not ProviderManifest:
        raise ValueError("manifest must be exact ProviderManifest")
    if type(decision) is not ProviderRouteDecision:
        raise ValueError("decision must be exact ProviderRouteDecision")
    if decision.state is RouteSelectionState.NO_ROUTE:
        raise ValueError("cannot prepare provider execution from NO_ROUTE")
    if decision.envelope_digest != envelope.digest:
        raise ValueError("route decision envelope mismatch")
    if decision.manifest_digest != manifest.digest:
        raise ValueError("route decision manifest mismatch")
    expected_route = ProviderRouteKey.from_manifest(manifest)
    if decision.route != expected_route:
        raise ValueError("route decision provider/model/adapter mismatch")
    if decision.qualification is None:
        raise ValueError("selected route is missing qualification")
    if decision.qualification.state is QualificationState.INELIGIBLE:
        raise ValueError("ineligible route cannot prepare execution")

    materialized = materialize_execution_request(
        envelope=envelope,
        manifest=manifest,
        instruction_text=instruction_text,
        input_bytes=input_bytes,
        state_blobs=state_blobs,
        provenance_resolver=provenance_resolver,
    )

    if materialized.qualification is not decision.qualification.state:
        raise ValueError("route/materialization qualification mismatch")

    plan = AdapterExecutionPlan(
        envelope_digest=envelope.digest,
        manifest_digest=manifest.digest,
        policy_digest=decision.policy_digest,
        provider_id=manifest.provider_id,
        model_id=manifest.model_id,
        adapter_version=manifest.adapter_version,
        route_state=decision.state,
        instruction_sha256=envelope.instruction_sha256,
        input_sha256=envelope.input_sha256,
        state_blobs=tuple(sorted(item.git_blob for item in envelope.state_refs)),
        prohibited_effects=tuple(sorted(envelope.prohibited_effects)),
        authority_scope=tuple(sorted(envelope.authority_scope)),
    )
    return PreparedAdapterExecution(plan=plan, materialized=materialized)


__all__ = [
    "AdapterExecutionPlan",
    "PreparedAdapterExecution",
    "prepare_adapter_execution",
]
