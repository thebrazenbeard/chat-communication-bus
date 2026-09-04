"""Topology-bound current writer-lane identity and validation primitives."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess


_WRITER_RE = re.compile(r"(?mi)^writer\s*:\s*(?P<value>.+?)\s*$")
_ZERO_SHA = "0" * 40


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


def _planned_successor_map(cutover_path: str | Path) -> dict[str, str]:
    try:
        raw = json.loads(Path(cutover_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WriterLaneError("WRITER_LANE_CUTOVER_INVALID") from exc
    planned = raw.get("planned_current_writer_lanes") if isinstance(raw, dict) else None
    if not isinstance(planned, dict) or not planned:
        raise WriterLaneError("WRITER_LANE_CUTOVER_PLANNED_MISSING")

    result: dict[str, str] = {}
    seen: set[str] = set()
    for identity, branch in planned.items():
        if not isinstance(identity, str) or not identity or not isinstance(branch, str) or not branch:
            raise WriterLaneError("WRITER_LANE_CUTOVER_PLANNED_INVALID")
        if branch in seen:
            raise WriterLaneError("DUPLICATE_PLANNED_WRITER_LANE_BRANCH")
        seen.add(branch)
        result[identity] = branch
    return result


def planned_successor_bootstrap_identity(
    ref: str,
    head: str,
    topology_path: str | Path,
    *,
    base: str | None,
    cutover_path: str | Path | None,
    bootstrap_main: str | None,
) -> str | None:
    """Return a planned successor identity only for its exact creation event.

    A successor is deliberately *not* active until the later topology-switch
    stage. The sole pre-switch exception is branch creation (zero ``before``
    SHA) from the exact canonical main commit supplied by the control checkout.
    """
    if base != _ZERO_SHA or cutover_path is None:
        return None

    branch = ref.removeprefix("refs/heads/")
    planned = _planned_successor_map(cutover_path)
    matches = [identity for identity, candidate in planned.items() if candidate == branch]
    if not matches:
        return None
    if len(matches) != 1:
        raise WriterLaneError("DUPLICATE_PLANNED_WRITER_LANE_BRANCH")

    identity = matches[0]
    lanes = load_writer_lanes(topology_path)
    if identity not in lanes:
        raise WriterLaneError("WRITER_LANE_CUTOVER_IDENTITY_UNKNOWN")
    if lanes[identity].branch == branch:
        return None
    if not bootstrap_main:
        raise WriterLaneError("WRITER_LANE_BOOTSTRAP_MAIN_REQUIRED")
    if head != bootstrap_main:
        raise WriterLaneError("WRITER_LANE_BOOTSTRAP_MAIN_MISMATCH")
    return identity


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


def _unwrap_scalar(value: str) -> str:
    text = value.strip()
    for left, right in (("`", "`"), ('"', '"'), ("'", "'")):
        if len(text) >= 2 and text.startswith(left) and text.endswith(right):
            return text[1:-1].strip()
    return text


def _declared_writer(repo_dir: Path, commit: str, path: str) -> str | None:
    content = _git_bytes(repo_dir, "show", f"{commit}:{path}")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WriterLaneError(f"WRITER_LANE_MESSAGE_NOT_UTF8:{path}") from exc
    match = _WRITER_RE.search(text)
    if not match:
        return None
    value = _unwrap_scalar(match.group("value"))
    return value or None


def _assert_ancestor(repo_dir: Path, base: str, head: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(repo_dir), "merge-base", "--is-ancestor", base, head],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise WriterLaneError("WRITER_LANE_BASE_NOT_ANCESTOR")


def _commits_to_validate(repo_dir: Path, head: str, base: str | None) -> list[str]:
    if not base or base == _ZERO_SHA:
        try:
            base = _git(repo_dir, "rev-parse", f"{head}^")
        except WriterLaneError as exc:
            raise WriterLaneError("WRITER_LANE_PARENT_REQUIRED") from exc
    _assert_ancestor(repo_dir, base, head)
    commits = [line for line in _git(repo_dir, "rev-list", "--reverse", f"{base}..{head}").splitlines() if line]
    if not commits:
        raise WriterLaneError("WRITER_LANE_NO_NEW_COMMITS")
    return commits


def _validate_commit_paths(repo_dir: Path, commit: str, expected_writer: str) -> None:
    parent_line = _git(repo_dir, "rev-list", "--parents", "-n", "1", commit).split()
    if len(parent_line) != 2:
        raise WriterLaneError("WRITER_LANE_MERGE_COMMIT_FORBIDDEN")
    parent = parent_line[1]

    raw = _git_bytes(
        repo_dir,
        "diff-tree",
        "--no-commit-id",
        "--name-status",
        "-r",
        "-z",
        parent,
        commit,
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
        declared = _declared_writer(repo_dir, commit, path)
        if declared is not None and declared.casefold() != expected_writer.casefold():
            raise WriterLaneError(
                f"WRITER_LANE_WRITER_MISMATCH:{path}:{declared}:{expected_writer}"
            )


def validate_writer_lane_commit(
    repo_dir: str | Path,
    ref: str,
    head: str,
    topology_path: str | Path,
    *,
    base: str | None = None,
    cutover_path: str | Path | None = None,
    bootstrap_main: str | None = None,
) -> str:
    lanes = load_writer_lanes(topology_path)
    repo = Path(repo_dir)
    if _git(repo, "rev-parse", "HEAD") != head:
        raise WriterLaneError("BRANCH_HEAD_MISMATCH")

    bootstrap_identity = planned_successor_bootstrap_identity(
        ref,
        head,
        topology_path,
        base=base,
        cutover_path=cutover_path,
        bootstrap_main=bootstrap_main,
    )
    if bootstrap_identity is not None:
        return bootstrap_identity

    identity = identity_for_ref(ref, topology_path)
    lane = lanes[identity]
    for commit in _commits_to_validate(repo, head, base):
        _validate_commit_paths(repo, commit, lane.writer)

    return identity


__all__ = [
    "WriterLane",
    "WriterLaneError",
    "identity_for_ref",
    "load_writer_lanes",
    "planned_successor_bootstrap_identity",
    "validate_writer_lane_commit",
]
