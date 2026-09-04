"""Topology-bound current writer-lane identity and validation primitives."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


class WriterLaneError(ValueError):
    pass


@dataclass(frozen=True)
class WriterLane:
    identity: str
    writer: str
    branch: str


def load_writer_lanes(topology_path: str | Path) -> dict[str, WriterLane]:
    raw = json.loads(Path(topology_path).read_text(encoding="utf-8"))
    required = raw.get("required_writer_lanes")
    if not isinstance(required, dict) or not required:
        raise WriterLaneError("WRITER_LANE_REGISTRY_MISSING")

    lanes: dict[str, WriterLane] = {}
    seen_branches: set[str] = set()
    for identity, record in required.items():
        if not isinstance(identity, str) or not identity or not isinstance(record, dict):
            raise WriterLaneError("WRITER_LANE_REGISTRY_INVALID")
        writer = record.get("writer")
        branch = record.get("branch")
        if not isinstance(writer, str) or not writer or not isinstance(branch, str) or not branch:
            raise WriterLaneError("WRITER_LANE_REGISTRY_INVALID")
        if branch in seen_branches:
            raise WriterLaneError("DUPLICATE_WRITER_LANE_BRANCH")
        seen_branches.add(branch)
        lanes[identity] = WriterLane(identity=identity, writer=writer, branch=branch)
    return lanes


def identity_for_ref(ref: str, topology_path: str | Path) -> str:
    branch = ref.removeprefix("refs/heads/")
    matches = [
        lane.identity
        for lane in load_writer_lanes(topology_path).values()
        if lane.branch == branch
    ]
    if len(matches) != 1:
        raise WriterLaneError("UNREGISTERED_WRITER_LANE")
    return matches[0]


__all__ = [
    "WriterLane",
    "WriterLaneError",
    "identity_for_ref",
    "load_writer_lanes",
]
