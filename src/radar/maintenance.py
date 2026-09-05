"""Exception-oriented Radar maintenance checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


class FindingCode(str, Enum):
    """Finding codes for radar maintenance checks."""

    MISSING_LANE = "MISSING_LANE"
    MALFORMED_LANE = "MALFORMED_LANE"
    DLQ_PENDING = "DLQ_PENDING"
    STALE_ENDPOINT = "STALE_ENDPOINT"
    STUCK_DEPENDENCY = "STUCK_DEPENDENCY"
    STALE_ACKNOWLEDGEMENT = "STALE_ACKNOWLEDGEMENT"
    PROTOCOL_DRIFT = "PROTOCOL_DRIFT"
    PROVIDER_MISMATCH = "PROVIDER_MISMATCH"
    CI_FAILED = "CI_FAILED"
    STALE_DOCS = "STALE_DOCS"
    ORPHANED_IDENTITY = "ORPHANED_IDENTITY"


class RadarState(TypedDict, total=False):
    """Type definition for radar state dictionary."""

    required_lanes: set[str]
    observed_lanes: set[str]
    malformed_lanes: tuple[str, ...]
    dlq_pending: int
    stale_endpoints: int
    stuck_dependencies: int
    stale_acknowledgements: int
    protocol_drift: bool
    provider_mismatch: bool
    ci_failed: bool
    stale_docs: bool
    orphaned_identities: tuple[str, ...]


@dataclass(frozen=True)
class MaintenanceFinding:
    code: str
    detail: str


def _check_missing_lanes(
    findings: list[MaintenanceFinding], state: RadarState
) -> None:
    """Check for required lanes that are not observed."""
    required = set(state.get("required_lanes", set()) or set())
    observed = set(state.get("observed_lanes", set()) or set())
    for identity in sorted(required - observed):
        findings.append(MaintenanceFinding(FindingCode.MISSING_LANE.value, identity))


def _check_malformed_lanes(
    findings: list[MaintenanceFinding], state: RadarState
) -> None:
    """Check for malformed lanes."""
    malformed = tuple(sorted(state.get("malformed_lanes", ()) or ()))
    for branch in malformed:
        findings.append(
            MaintenanceFinding(FindingCode.MALFORMED_LANE.value, str(branch))
        )


def _check_positive_count(
    findings: list[MaintenanceFinding],
    code: FindingCode,
    state: RadarState,
    key: str,
) -> None:
    """Check if a count value is positive and add a finding if so."""
    value = int(state.get(key, 0) or 0)  # type: ignore
    if value > 0:
        findings.append(MaintenanceFinding(code.value, str(value)))


def _check_boolean_flags(
    findings: list[MaintenanceFinding], state: RadarState
) -> None:
    """Check boolean flags for system issues."""
    boolean_checks = [
        ("protocol_drift", FindingCode.PROTOCOL_DRIFT, "current pointer differs"),
        (
            "provider_mismatch",
            FindingCode.PROVIDER_MISMATCH,
            "provider projection differs",
        ),
        ("ci_failed", FindingCode.CI_FAILED, "current integration head is red"),
        ("stale_docs", FindingCode.STALE_DOCS, "current pointers or docs are stale"),
    ]

    for state_key, code, detail in boolean_checks:
        if state.get(state_key, False):  # type: ignore
            findings.append(MaintenanceFinding(code.value, detail))


def _check_orphaned_identities(
    findings: list[MaintenanceFinding], state: RadarState
) -> None:
    """Check for orphaned identities."""
    orphaned = tuple(sorted(state.get("orphaned_identities", ()) or ()))
    for identity in orphaned:
        findings.append(
            MaintenanceFinding(FindingCode.ORPHANED_IDENTITY.value, str(identity))
        )


def audit(state: dict[str, object]) -> tuple[MaintenanceFinding, ...]:
    """Audit radar state and return findings about system health.

    Args:
        state: Radar state dictionary containing lane, endpoint, and dependency info.

    Returns:
        Tuple of MaintenanceFinding objects documenting any issues found.

    Example:
        >>> findings = audit({"required_lanes": {"a", "b"}, "observed_lanes": {"a"}})
        >>> findings[0].code
        'MISSING_LANE'
    """
    findings: list[MaintenanceFinding] = []

    _check_missing_lanes(findings, state)  # type: ignore
    _check_malformed_lanes(findings, state)  # type: ignore
    _check_positive_count(findings, FindingCode.DLQ_PENDING, state, "dlq_pending")  # type: ignore
    _check_positive_count(findings, FindingCode.STALE_ENDPOINT, state, "stale_endpoints")  # type: ignore
    _check_positive_count(findings, FindingCode.STUCK_DEPENDENCY, state, "stuck_dependencies")  # type: ignore
    _check_positive_count(findings, FindingCode.STALE_ACKNOWLEDGEMENT, state, "stale_acknowledgements")  # type: ignore
    _check_boolean_flags(findings, state)  # type: ignore
    _check_orphaned_identities(findings, state)  # type: ignore

    return tuple(findings)


__all__ = ["FindingCode", "MaintenanceFinding", "RadarState", "audit"]
