"""Topology-bound current writer-lane identity and validation primitives."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess


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


def _git(repo_dir: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo_dir), *args],
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() if exc.stderr else str(exc)
        raise WriterLaneError(f"GIT_COMMAND_FAILED:{detail}") from exc


def _git_bytes(repo_dir: Path, *args: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo_dir), *args],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip() if exc.stderr else str(exc)
        raise WriterLaneError(f"GIT_COMMAND_FAILED:{detail}") from exc


def validate_writer_lane_commit(
    repo_dir: str | Path,
    ref: str,
    head: str,
    topology_path: str | Path,
) -> str:
    identity = identity_for_ref(ref, topology_path)
    repo = Path(repo_dir)
    if _git(repo, "rev-parse", "HEAD") != head:
        raise WriterLaneError("BRANCH_HEAD_MISMATCH")

    try:
        parent = _git(repo, "rev-parse", f"{head}^")
    except WriterLaneError as exc:
        raise WriterLaneError("WRITER_LANE_PARENT_REQUIRED") from exc

    raw = _git_bytes(
        repo,
        "diff-tree",
        "--no-commit-id",
        "--name-status",
        "-r",
        "-z",
        parent,
        head,
    )
    fields = [value.decode("utf-8") for value in raw.split(b"\0") if value]
    if len(fields) % 2 != 0:
        raise WriterLaneError("WRITER_LANE_DIFF_INVALID")

    for index in range(0, len(fields), 2):
        status, path = fields[index : index + 2]
        if not path.startswith("messages/") or not path.endswith(".md"):
            raise WriterLaneError(f"WRITER_LANE_PATH_FORBIDDEN:{path}")
        if status != "A":
            raise WriterLaneError(f"WRITER_LANE_MESSAGE_NOT_APPEND_ONLY:{path}")

    return identity


__all__ = [
    "WriterLane",
    "WriterLaneError",
    "identity_for_ref",
    "load_writer_lanes",
    "validate_writer_lane_commit",
]
