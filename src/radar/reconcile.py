"""Compare durable GitHub state with rebuildable provider projections."""

from __future__ import annotations

from dataclasses import dataclass


SAFE_PROJECTION_REPAIR = "SAFE_PROJECTION_REPAIR"
AMBIGUOUS_DURABLE_CONFLICT = "AMBIGUOUS_DURABLE_CONFLICT"
OBSERVATION_ONLY = "OBSERVATION_ONLY"


@dataclass(frozen=True)
class Finding:
    code: str
    repair_class: str
    detail: str


class Reconciler:
    def compare(self, github_state: dict[str, object], provider_state: dict[str, object]) -> tuple[Finding, ...]:
        findings: list[Finding] = []

        github_protocol = github_state.get("protocol_head")
        provider_protocol = provider_state.get("protocol_head")
        if github_protocol != provider_protocol:
            findings.append(
                Finding(
                    "PROTOCOL_HEAD_DRIFT",
                    SAFE_PROJECTION_REPAIR,
                    f"provider={provider_protocol!r} github={github_protocol!r}",
                )
            )

        github_lanes = dict(github_state.get("lanes", {}) or {})
        provider_lanes = dict(provider_state.get("lanes", {}) or {})

        for identity, github_lane in sorted(github_lanes.items()):
            provider_lane = provider_lanes.get(identity)
            if provider_lane is None:
                findings.append(
                    Finding(
                        "MISSING_PROVIDER_LANE",
                        SAFE_PROJECTION_REPAIR,
                        f"{identity}:{github_lane}",
                    )
                )
                continue
            if isinstance(provider_lane, (list, tuple, set)):
                claims = tuple(provider_lane)
                if len(set(claims)) > 1:
                    findings.append(
                        Finding(
                            "MULTIPLE_WRITER_CLAIMS",
                            AMBIGUOUS_DURABLE_CONFLICT,
                            f"{identity}:{claims!r}",
                        )
                    )
                    continue
            elif provider_lane != github_lane:
                findings.append(
                    Finding(
                        "LANE_PROJECTION_DRIFT",
                        SAFE_PROJECTION_REPAIR,
                        f"{identity}:provider={provider_lane!r} github={github_lane!r}",
                    )
                )

        for identity in sorted(set(provider_lanes) - set(github_lanes)):
            provider_lane = provider_lanes[identity]
            if isinstance(provider_lane, (list, tuple, set)) and len(set(provider_lane)) > 1:
                findings.append(
                    Finding(
                        "MULTIPLE_WRITER_CLAIMS",
                        AMBIGUOUS_DURABLE_CONFLICT,
                        f"{identity}:{tuple(provider_lane)!r}",
                    )
                )
            else:
                findings.append(
                    Finding(
                        "ORPHANED_PROVIDER_LANE",
                        SAFE_PROJECTION_REPAIR,
                        f"{identity}:{provider_lane!r}",
                    )
                )

        return tuple(findings)


__all__ = [
    "AMBIGUOUS_DURABLE_CONFLICT",
    "Finding",
    "OBSERVATION_ONLY",
    "Reconciler",
    "SAFE_PROJECTION_REPAIR",
]
