#!/usr/bin/env python3
"""Validate-only entrypoint for Radar's immutable trusted reconciler.

This script performs no provider write. Caller event fields are wake-up hints only;
canonical lane identity, observed head, activation anchor, and ancestry are derived
from the trusted source checkout and Git object database. Writer branches are read
directly from fetched origin remote-tracking refs; validate-only reconciliation does
not create or move local branch refs.
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

from radar.trusted_lane_validation import validate_active_writer_range  # noqa: E402
from radar.trusted_reconciler import (  # noqa: E402
    AncestryDisposition,
    LocalGitRepository,
    ReconcileError,
    TrustedReconciler,
)
from radar.trusted_wakeup import load_caller_event, requested_identities  # noqa: E402
from radar.writer_lanes import WriterLaneError  # noqa: E402


class UninitializedCursorJournal:
    """Validate-only cursor view; provider-capable projection uses durable state."""

    def projected_head(self, identity: str, branch: str) -> None:
        return None


def build_validation_report(
    *,
    repo_dir: Path,
    topology_path: Path,
    cutover_path: Path,
    event_name: str,
    event: dict[str, object],
    repository: str,
) -> dict[str, object]:
    identities, observed_hint = requested_identities(
        event_name=event_name,
        event=event,
        topology_path=topology_path,
        repository=repository,
    )
    reconciler = TrustedReconciler(
        topology_path=topology_path,
        cutover_path=cutover_path,
        git_repository=LocalGitRepository(repo_dir, use_remote_tracking_refs=True),
        journal=UninitializedCursorJournal(),
    )

    targets: list[dict[str, object]] = []
    for identity in identities:
        target = reconciler.derive_target(identity)
        row = asdict(target)
        row["disposition"] = target.disposition.value
        row["writer_range_validated"] = False
        if observed_hint is not None:
            row["workflow_run_head_hint"] = observed_hint
            row["hint_matches_observed_head"] = observed_hint == target.observed_head

        if target.disposition is AncestryDisposition.DIVERGED_HISTORY:
            raise ReconcileError(f"DIVERGED_HISTORY:{identity}:{target.branch}")

        if target.disposition is AncestryDisposition.FORWARD:
            commits = validate_active_writer_range(
                repo_dir,
                identity=identity,
                base=target.base_head,
                head=target.observed_head,
                topology_path=topology_path,
                cutover_path=cutover_path,
            )
            if commits != target.commits:
                raise ReconcileError("TRUSTED_RANGE_MISMATCH")
            row["writer_range_validated"] = True

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

    if os.environ.get("RADAR_RECONCILE_MODE") != "validate-only":
        raise ReconcileError("VALIDATE_ONLY_MODE_REQUIRED")
    if not args.event_path or not args.event_name or not args.repository:
        raise ReconcileError("CALLER_CONTEXT_REQUIRED")

    repo_dir = Path(args.repo_dir)
    report = build_validation_report(
        repo_dir=repo_dir,
        topology_path=Path(args.topology),
        cutover_path=Path(args.cutover),
        event_name=args.event_name,
        event=load_caller_event(args.event_path),
        repository=args.repository,
    )
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ReconcileError, WriterLaneError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
