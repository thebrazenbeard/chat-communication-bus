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
from radar.trusted_wakeup import (  # noqa: E402
    load_caller_event,
    materialize_inert_remote_bus_refs,
    requested_identities,
)


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

    if os.environ.get("RADAR_RECONCILE_MODE") != "validate-only":
        raise ReconcileError("VALIDATE_ONLY_MODE_REQUIRED")
    if not args.event_path or not args.event_name or not args.repository:
        raise ReconcileError("CALLER_CONTEXT_REQUIRED")

    repo_dir = Path(args.repo_dir)
    materialize_inert_remote_bus_refs(repo_dir)
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
    raise SystemExit(main())
