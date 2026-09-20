"""Deterministic provider-route selection for portable Vera execution.

Routing is capability matching under an explicit user/operator policy.  It does
not grant effect authority, infer preference for "less restricted" providers, or
silently weaken an execution envelope.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import json
from typing import Iterable

from .provider_portability import (
    PortableExecutionEnvelope,
    ProviderManifest,
    ProviderQualification,
    QualificationState,
    qualify_provider,
)


def _nonempty(value: str, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{label} must be a non-empty exact string")
    return value


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True, order=True)
class ProviderRouteKey:
    provider_id: str
    model_id: str
    adapter_version: str

    def __post_init__(self) -> None:
        _nonempty(self.provider_id, "provider_id")
        _nonempty(self.model_id, "model_id")
        _nonempty(self.adapter_version, "adapter_version")

    @classmethod
    def from_manifest(cls, manifest: ProviderManifest) -> "ProviderRouteKey":
        if type(manifest) is not ProviderManifest:
            raise ValueError("manifest must be exact ProviderManifest")
        return cls(
            provider_id=manifest.provider_id,
            model_id=manifest.model_id,
            adapter_version=manifest.adapter_version,
        )

    def payload(self) -> dict[str, str]:
        return {
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "adapter_version": self.adapter_version,
        }


@dataclass(frozen=True)
class ProviderRoutePolicy:
    policy_id: str
    ordered_routes: tuple[ProviderRouteKey, ...]
    allow_degraded: bool = False

    def __post_init__(self) -> None:
        _nonempty(self.policy_id, "policy_id")
        if type(self.ordered_routes) is not tuple:
            raise ValueError("ordered_routes must be a tuple")
        if not self.ordered_routes:
            raise ValueError("ordered_routes must not be empty")
        if any(type(item) is not ProviderRouteKey for item in self.ordered_routes):
            raise ValueError("ordered_routes must contain exact ProviderRouteKey values")
        if len(self.ordered_routes) != len(set(self.ordered_routes)):
            raise ValueError("ordered_routes must be unique")
        if type(self.allow_degraded) is not bool:
            raise ValueError("allow_degraded must be exact bool")

    def payload(self) -> dict[str, object]:
        return {
            "schema": "VERA_PROVIDER_ROUTE_POLICY_V1",
            "policy_id": self.policy_id,
            "ordered_routes": [item.payload() for item in self.ordered_routes],
            "allow_degraded": self.allow_degraded,
        }

    @property
    def digest(self) -> str:
        return _digest(self.payload())


class RouteSelectionState(StrEnum):
    SELECTED_ELIGIBLE = "SELECTED_ELIGIBLE"
    SELECTED_DEGRADED = "SELECTED_DEGRADED"
    NO_ROUTE = "NO_ROUTE"


@dataclass(frozen=True)
class ProviderRouteDecision:
    state: RouteSelectionState
    policy_digest: str
    envelope_digest: str
    route: ProviderRouteKey | None
    manifest_digest: str | None
    qualification: ProviderQualification | None
    decision_claim: str = "ROUTE_SELECTION_ONLY_NO_EFFECT_AUTHORITY"

    def __post_init__(self) -> None:
        if self.decision_claim != "ROUTE_SELECTION_ONLY_NO_EFFECT_AUTHORITY":
            raise ValueError("unsupported route decision claim")
        if self.state is RouteSelectionState.NO_ROUTE:
            if (
                self.route is not None
                or self.manifest_digest is not None
                or self.qualification is not None
            ):
                raise ValueError("NO_ROUTE cannot carry a selected route")
        else:
            if type(self.route) is not ProviderRouteKey:
                raise ValueError("selected route requires exact ProviderRouteKey")
            if type(self.manifest_digest) is not str:
                raise ValueError("selected route requires manifest digest")
            if type(self.qualification) is not ProviderQualification:
                raise ValueError("selected route requires qualification")


def select_provider_route(
    *,
    envelope: PortableExecutionEnvelope,
    manifests: Iterable[ProviderManifest],
    policy: ProviderRoutePolicy,
) -> ProviderRouteDecision:
    if type(envelope) is not PortableExecutionEnvelope:
        raise ValueError("envelope must be exact PortableExecutionEnvelope")
    if type(policy) is not ProviderRoutePolicy:
        raise ValueError("policy must be exact ProviderRoutePolicy")

    by_route: dict[ProviderRouteKey, ProviderManifest] = {}
    for manifest in manifests:
        if type(manifest) is not ProviderManifest:
            raise ValueError("manifests must contain exact ProviderManifest values")
        route = ProviderRouteKey.from_manifest(manifest)
        if route in by_route:
            raise ValueError("duplicate provider route manifest")
        by_route[route] = manifest

    eligible: list[
        tuple[ProviderRouteKey, ProviderManifest, ProviderQualification]
    ] = []
    degraded: list[
        tuple[ProviderRouteKey, ProviderManifest, ProviderQualification]
    ] = []

    for route in policy.ordered_routes:
        manifest = by_route.get(route)
        if manifest is None:
            continue
        qualification = qualify_provider(envelope, manifest)
        if qualification.state is QualificationState.ELIGIBLE:
            eligible.append((route, manifest, qualification))
        elif qualification.state is QualificationState.DEGRADED:
            degraded.append((route, manifest, qualification))

    if eligible:
        route, manifest, qualification = eligible[0]
        return ProviderRouteDecision(
            state=RouteSelectionState.SELECTED_ELIGIBLE,
            policy_digest=policy.digest,
            envelope_digest=envelope.digest,
            route=route,
            manifest_digest=manifest.digest,
            qualification=qualification,
        )

    if policy.allow_degraded and degraded:
        route, manifest, qualification = degraded[0]
        return ProviderRouteDecision(
            state=RouteSelectionState.SELECTED_DEGRADED,
            policy_digest=policy.digest,
            envelope_digest=envelope.digest,
            route=route,
            manifest_digest=manifest.digest,
            qualification=qualification,
        )

    return ProviderRouteDecision(
        state=RouteSelectionState.NO_ROUTE,
        policy_digest=policy.digest,
        envelope_digest=envelope.digest,
        route=None,
        manifest_digest=None,
        qualification=None,
    )


__all__ = [
    "ProviderRouteDecision",
    "ProviderRouteKey",
    "ProviderRoutePolicy",
    "RouteSelectionState",
    "select_provider_route",
]
