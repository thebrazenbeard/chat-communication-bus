"""Pure GitHub-state projection helpers for Radar."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Mapping


_LANE_RE = re.compile(r"^bus/(?P<identity>[a-z0-9_-]+)-v\d+$")
_ALIASES = {
    "bridget": "brigit",
    "vera-sol": "vera",
}


def _normalize_identity(value: str) -> str:
    key = value.strip().casefold()
    return _ALIASES.get(key, key)


@dataclass(frozen=True)
class LaneEvidence:
    """Transport-neutral structural evidence for a candidate writer lane."""

    has_messages_dir: bool
    declared_writer: str | None = None
    message_writers: tuple[str, ...] = ()

    def supports(self, identity: str) -> bool:
        expected = _normalize_identity(identity)
        if self.declared_writer and _normalize_identity(self.declared_writer) == expected:
            return True
        return any(_normalize_identity(writer) == expected for writer in self.message_writers)


@dataclass(frozen=True)
class RepositoryProjection:
    observed_branches: tuple[str, ...]
    identity_lanes: dict[str, str]
    missing_required: tuple[str, ...]
    protocol_branches: tuple[str, ...]
    malformed_lanes: tuple[str, ...] = ()


def project_branches(
    branch_names: Iterable[str],
    *,
    required_identities: set[str] | frozenset[str] = frozenset(),
    lane_evidence: Mapping[str, LaneEvidence] | None = None,
) -> RepositoryProjection:
    """Project writer-lane candidates, optionally validating mailbox evidence.

    Without ``lane_evidence`` this remains a discovery-only compatibility path.
    When evidence is supplied, every candidate writer lane must have a real
    messages directory and evidence tying the lane to its expected logical
    writer. Invalid/unverified candidates are surfaced as malformed and are not
    counted as healthy lanes.
    """

    observed = tuple(sorted(set(branch_names)))
    lanes: dict[str, str] = {}
    protocols: list[str] = []
    malformed: list[str] = []

    for branch in observed:
        if branch.startswith("bus/protocol-v"):
            protocols.append(branch)
            continue
        match = _LANE_RE.match(branch)
        if not match:
            continue
        raw_identity = match.group("identity")
        identity = _normalize_identity(raw_identity)

        if lane_evidence is not None:
            evidence = lane_evidence.get(branch)
            if evidence is None or not evidence.has_messages_dir or not evidence.supports(identity):
                malformed.append(branch)
                continue

        existing = lanes.get(identity)
        if existing is None:
            lanes[identity] = branch
        elif existing != branch:
            # Preserve the first deterministic branch in the projection; the
            # reconciler/maintenance layer is responsible for surfacing a
            # multiple-writer conflict instead of silently picking authority.
            lanes[identity] = min(existing, branch)

    required = {_normalize_identity(identity) for identity in required_identities}
    missing = tuple(sorted(required - set(lanes)))
    return RepositoryProjection(
        observed_branches=observed,
        identity_lanes=lanes,
        missing_required=missing,
        protocol_branches=tuple(sorted(protocols)),
        malformed_lanes=tuple(sorted(malformed)),
    )


__all__ = ["LaneEvidence", "RepositoryProjection", "project_branches"]
