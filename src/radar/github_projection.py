"""Pure GitHub-state projection helpers for Radar."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


_LANE_RE = re.compile(r"^bus/(?P<identity>[a-z0-9_-]+)-v\d+$")
_ALIASES = {
    "bridget": "brigit",
    "vera-sol": "vera",
}


@dataclass(frozen=True)
class RepositoryProjection:
    observed_branches: tuple[str, ...]
    identity_lanes: dict[str, str]
    missing_required: tuple[str, ...]
    protocol_branches: tuple[str, ...]


def project_branches(
    branch_names: Iterable[str], *, required_identities: set[str] | frozenset[str] = frozenset()
) -> RepositoryProjection:
    observed = tuple(sorted(set(branch_names)))
    lanes: dict[str, str] = {}
    protocols: list[str] = []

    for branch in observed:
        if branch.startswith("bus/protocol-v"):
            protocols.append(branch)
            continue
        match = _LANE_RE.match(branch)
        if not match:
            continue
        raw_identity = match.group("identity")
        identity = _ALIASES.get(raw_identity, raw_identity)
        existing = lanes.get(identity)
        if existing is None:
            lanes[identity] = branch
        elif existing != branch:
            # Preserve the first deterministic branch in the projection; the
            # reconciler/maintenance layer is responsible for surfacing a
            # multiple-writer conflict instead of silently picking authority.
            lanes[identity] = min(existing, branch)

    required = {_ALIASES.get(i.casefold(), i.casefold()) for i in required_identities}
    missing = tuple(sorted(required - set(lanes)))
    return RepositoryProjection(
        observed_branches=observed,
        identity_lanes=lanes,
        missing_required=missing,
        protocol_branches=tuple(sorted(protocols)),
    )


__all__ = ["RepositoryProjection", "project_branches"]
