#!/usr/bin/env python3
"""Fail-closed source/currentness audit of ACTIVE Bus lane Git tree paths."""

from __future__ import annotations

import argparse
from pathlib import Path

from radar.active_lane_mailboxes import ActiveMailboxAuditError, audit_active_lane_mailboxes


ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", default=str(ROOT))
    parser.add_argument("--topology", default=str(ROOT / "architecture/contracts/RADAR_TOPOLOGY_V1.json"))
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--identity", help="One ACTIVE identity; default checks all ACTIVE lanes")
    args = parser.parse_args(argv)
    try:
        heads = audit_active_lane_mailboxes(
            args.repo_dir, args.topology, remote=args.remote, identity=args.identity
        )
    except ActiveMailboxAuditError as exc:
        print(str(exc))
        return 1
    for identity, head in sorted(heads.items()):
        print(f"ACTIVE_MAILBOX_STRUCTURAL_ONLY:{identity}:{head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
