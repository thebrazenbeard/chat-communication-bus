"""Compare durable GitHub state with rebuildable provider projections."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# Type alias for lane values
LaneValue = str | list | tuple | set | dict[str, object]

SAFE_PROJECTION_REPAIR = "SAFE_PROJECTION_REPAIR"
AMBIGUOUS_DURABLE_CONFLICT = "AMBIGUOUS_DURABLE_CONFLICT"
OBSERVATION_ONLY = "OBSERVATION_ONLY"


@dataclass(frozen=True)
class Finding:
    """Represents a discrepancy between GitHub and provider state.
    
    Attributes:
        code: Finding classification code (e.g., "PROTOCOL_HEAD_DRIFT")
        repair_class: Category indicating how to handle this finding
        detail: Human-readable details about the discrepancy
    """

    code: str
    repair_class: str
    detail: str


class Reconciler:
    """Compares durable GitHub state against provider projections to detect drift.
    
    Reconciliation identifies discrepancies in protocol versions and lane states
    between the source-of-truth GitHub state and projections from external providers.
    """

    def compare(
        self,
        github_state: dict[str, object] | None,
        provider_state: dict[str, object] | None,
    ) -> tuple[Finding, ...]:
        """Identify discrepancies between GitHub and provider state.

        Args:
            github_state: Source-of-truth state from GitHub. If None, treated as empty.
            provider_state: Projected state from external provider. If None, treated as empty.

        Returns:
            Tuple of findings describing all discrepancies found.
        """
        findings: list[Finding] = []

        # Handle None inputs gracefully
        if github_state is None:
            github_state = {}
        if provider_state is None:
            provider_state = {}

        # Compare protocol versions
        self._reconcile_protocol_head(github_state, provider_state, findings)

        # Compare lane states
        self._reconcile_lanes(github_state, provider_state, findings)

        return tuple(findings)

    def _reconcile_protocol_head(
        self,
        github_state: dict[str, object],
        provider_state: dict[str, object],
        findings: list[Finding],
    ) -> None:
        """Detect protocol version drift between states."""
        github_protocol = github_state.get("protocol_head")
        provider_protocol = provider_state.get("protocol_head")
        if github_protocol != provider_protocol:
            finding = Finding(
                "PROTOCOL_HEAD_DRIFT",
                SAFE_PROJECTION_REPAIR,
                f"provider={provider_protocol!r} github={github_protocol!r}",
            )
            findings.append(finding)
            logger.debug(f"Protocol drift detected: {finding.detail}")

    def _reconcile_lanes(
        self,
        github_state: dict[str, object],
        provider_state: dict[str, object],
        findings: list[Finding],
    ) -> None:
        """Detect lane state discrepancies between GitHub and provider."""
        github_lanes = dict(github_state.get("lanes", {}) or {})
        provider_lanes = dict(provider_state.get("lanes", {}) or {})

        # Check lanes present in GitHub state
        for identity, github_lane in sorted(github_lanes.items()):
            provider_lane = provider_lanes.get(identity)
            if provider_lane is None:
                finding = Finding(
                    "MISSING_PROVIDER_LANE",
                    SAFE_PROJECTION_REPAIR,
                    f"{identity}:{github_lane}",
                )
                findings.append(finding)
                logger.debug(f"Missing lane: {finding.detail}")
                continue

            finding = self._reconcile_lane(identity, github_lane, provider_lane)
            if finding:
                findings.append(finding)
                logger.debug(f"Lane drift: {finding.detail}")

        # Check lanes present only in provider state
        for identity in sorted(set(provider_lanes) - set(github_lanes)):
            provider_lane = provider_lanes[identity]
            finding = self._handle_orphaned_lane(identity, provider_lane)
            if finding:
                findings.append(finding)
                logger.debug(f"Orphaned lane: {finding.detail}")

    def _is_multi_valued_lane(self, lane: object) -> bool:
        """Check if a lane value contains multiple claims (list, tuple, or set)."""
        return isinstance(lane, (list, tuple, set))

    def _get_unique_claims(self, lane: object) -> set[Any]:
        """Extract unique claims from a lane value."""
        if self._is_multi_valued_lane(lane):
            return set(lane)
        return {lane}

    def _reconcile_lane(
        self,
        identity: str,
        github_lane: object,
        provider_lane: object,
    ) -> Finding | None:
        """Compare a single lane between GitHub and provider states.

        Args:
            identity: The lane identifier
            github_lane: The GitHub state for this lane
            provider_lane: The provider state for this lane

        Returns:
            Finding if discrepancy detected, None otherwise.
        """
        # Check for multiple conflicting claims in provider lane
        if self._is_multi_valued_lane(provider_lane):
            unique_claims = self._get_unique_claims(provider_lane)
            if len(unique_claims) > 1:
                return Finding(
                    "MULTIPLE_WRITER_CLAIMS",
                    AMBIGUOUS_DURABLE_CONFLICT,
                    f"{identity}:{tuple(unique_claims)!r}",
                )
            # Single claim in multi-valued lane; compare against GitHub
            provider_lane = next(iter(unique_claims))

        # Check for state drift
        if provider_lane != github_lane:
            return Finding(
                "LANE_PROJECTION_DRIFT",
                SAFE_PROJECTION_REPAIR,
                f"{identity}:provider={provider_lane!r} github={github_lane!r}",
            )

        return None

    def _handle_orphaned_lane(self, identity: str, provider_lane: object) -> Finding | None:
        """Handle a lane present only in provider state.

        Args:
            identity: The lane identifier
            provider_lane: The provider state for this lane

        Returns:
            Finding describing the orphaned lane.
        """
        # Check for multiple conflicting claims
        if self._is_multi_valued_lane(provider_lane):
            unique_claims = self._get_unique_claims(provider_lane)
            if len(unique_claims) > 1:
                return Finding(
                    "MULTIPLE_WRITER_CLAIMS",
                    AMBIGUOUS_DURABLE_CONFLICT,
                    f"{identity}:{tuple(unique_claims)!r}",
                )

        return Finding(
            "ORPHANED_PROVIDER_LANE",
            SAFE_PROJECTION_REPAIR,
            f"{identity}:{provider_lane!r}",
        )


__all__ = [
    "AMBIGUOUS_DURABLE_CONFLICT",
    "Finding",
    "OBSERVATION_ONLY",
    "Reconciler",
    "SAFE_PROJECTION_REPAIR",
]
