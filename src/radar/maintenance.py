"""Exception-oriented Radar maintenance checks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MaintenanceFinding:
    code: str
    detail: str


def audit(state: dict[str, object]) -> tuple[MaintenanceFinding, ...]:
    findings: list[MaintenanceFinding] = []

    required = set(state.get("required_lanes", set()) or set())
    observed = set(state.get("observed_lanes", set()) or set())
    for identity in sorted(required - observed):
        findings.append(MaintenanceFinding("MISSING_LANE", identity))

    pending = int(state.get("dlq_pending", 0) or 0)
    if pending > 0:
        findings.append(MaintenanceFinding("DLQ_PENDING", str(pending)))

    stale_endpoints = int(state.get("stale_endpoints", 0) or 0)
    if stale_endpoints > 0:
        findings.append(MaintenanceFinding("STALE_ENDPOINT", str(stale_endpoints)))

    stuck_dependencies = int(state.get("stuck_dependencies", 0) or 0)
    if stuck_dependencies > 0:
        findings.append(MaintenanceFinding("STUCK_DEPENDENCY", str(stuck_dependencies)))

    stale_acknowledgements = int(state.get("stale_acknowledgements", 0) or 0)
    if stale_acknowledgements > 0:
        findings.append(MaintenanceFinding("STALE_ACKNOWLEDGEMENT", str(stale_acknowledgements)))

    if bool(state.get("protocol_drift", False)):
        findings.append(MaintenanceFinding("PROTOCOL_DRIFT", "current pointer differs"))

    if bool(state.get("provider_mismatch", False)):
        findings.append(MaintenanceFinding("PROVIDER_MISMATCH", "provider projection differs"))

    if bool(state.get("ci_failed", False)):
        findings.append(MaintenanceFinding("CI_FAILED", "current integration head is red"))

    if bool(state.get("stale_docs", False)):
        findings.append(MaintenanceFinding("STALE_DOCS", "current pointers or docs are stale"))

    orphaned = tuple(sorted(state.get("orphaned_identities", ()) or ()))
    for identity in orphaned:
        findings.append(MaintenanceFinding("ORPHANED_IDENTITY", str(identity)))

    return tuple(findings)


__all__ = ["MaintenanceFinding", "audit"]
