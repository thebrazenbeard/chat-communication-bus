#!/usr/bin/env python3
"""Validate-only entrypoint for Radar's immutable trusted reconciler.

This script performs no provider write. Caller event fields are wake-up hints only;
canonical lane identity, observed head, activation anchor, and ancestry are derived
from the trusted source checkout and Git object database.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from radar.trusted_reconciler import LocalGitRepository, ReconcileError, TrustedReconciler  # noqa: E402
from radar.writer_lanes import load_writer_lanes  # noqa: E402


EXPECTED_REPOSITORY = "thebrazenbeard/chat-communication-bus"
_ALLOWED_EVENT_NAMES = frozenset({"workflow_run", "schedule"})


class UninitializedCursorJournal:
    """Task-8 validate-only cursor view; Task 9 wires durable provider state."""

    def projected_head(self, identity: str, branch: str) -> None:
        return None


def _load_event(path: Path) -> dict[str, object]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReconcileError("CALLER_EVENT_INVALID") from exc
    if not isinstance(raw, dict):
        raise ReconcileError("CALLER_EVENT_INVALID")
    return raw


def _active_identity_for_branch(topology_path: Path, branch: str) -> str:
    lanes = load_writer_lanes(topology_path)
    matches = [identity for identity, lane in lanes.items() if lane.branch == branch]
    if len(matches) != 1:
        raise ReconcileError("WAKEUP_BRANCH_NOT_ACTIVE")
    return matches[0]


def _requested_identities(
    *,
    event_name: str,
    event: dict[str, object],
    topology_path: Path,
) -> tuple[tuple[str, ...], str | None]:
    if event_name == "schedule":
        return tuple(sorted(load_writer_lanes(topology_path))), None

    workflow_run = event.get("workflow_run")
    if not isinstance(workflow_run, dict):
        raise ReconcileError("WORKFLOW_RUN_EVENT_INVALID")
    head_branch = workflow_run.get("head_branch")
    head_sha = workflow_run.get("head_sha")
    if not isinstance(head_branch, str) or not head_branch:
        raise ReconcileError("WORKFLOW_RUN_BRANCH_INVALID")
    if not isinstance(head_sha, str) or not head_sha:
        raise ReconcileError("WORKFLOW_RUN_HEAD_INVALID")
    return (_active_identity_for_branch(topology_path, head_branch),), head_sha


def build_validation_report(
    *,
    repo_dir: Path,
    topology_path: Path,
    cutover_path: Path,
    event_name: str,
    event: dict[str, object],
    repository: str,
) -> dict[str, object]:
    if repository != EXPECTED_REPOSITORY:
        raise ReconcileError("UNTRUSTED_CALLER_REPOSITORY")
    if event_name not in _ALLOWED_EVENT_NAMES:
        raise ReconcileError("UNSUPPORTED_CALLER_EVENT")

    identities, observed_hint = _requested_identities(
        event_name=event_name,
        event=event,
        topology_path=topology_path,
    )
    reconciler = TrustedReconciler(
        topology_path=topology_path,
        cutover_path=cutover_path,
        git_repository=LocalGitRepository(repo_dir),
        journal=UninitializedCursorJournal(),
    )

    targets: list[dict[str, object]] = []
    for identity in identities:
        target = reconciler.derive_target(identity)
        row = asdict(target)
        row["disposition"] = target.disposition.value
        if observed_hint is not None:
            row["workflow_run_head_hint"] = observed_hint
            row["hint_matches_observed_head"] = observed_hint == target.observed_head
        targets.append(row)

    return {
        "mode": "validate-only",
        "event_name": event_name,
        "repository": repository,
        "targets": targets,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", default=str(ROOT))
    parser.add_argument(
        "--topology",
        default=str(ROOT / "architecture/contracts/RADAR_TOPOLOGY_V1.json"),
    )
    parser.add_argument(
        "--cutover",
        default=str(ROOT / "architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json"),
    )
    parser.add_argument("--event-path", default=os.environ.get("GITHUB_EVENT_PATH"))
    parser.add_argument("--event-name", default=os.environ.get("GITHUB_EVENT_NAME"))
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    args = parser.parse_args()

    if not args.event_path or not args.event_name or not args.repository:
        raise ReconcileError("CALLER_CONTEXT_REQUIRED")

    report = build_validation_report(
        repo_dir=Path(args.repo_dir),
        topology_path=Path(args.topology),
        cutover_path=Path(args.cutover),
        event_name=args.event_name,
        event=_load_event(Path(args.event_path)),
        repository=args.repository,
    )
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
