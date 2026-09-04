#!/usr/bin/env python3
"""Fail closed when a current writer-lane push is not mailbox-only append."""

from __future__ import annotations

import argparse
from pathlib import Path

from radar.writer_lanes import WriterLaneError, validate_writer_lane_commit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOPOLOGY = ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", default=".")
    parser.add_argument("--ref", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base")
    parser.add_argument("--topology", default=str(DEFAULT_TOPOLOGY))
    args = parser.parse_args(argv)

    try:
        identity = validate_writer_lane_commit(
            args.repo_dir,
            args.ref,
            args.head,
            args.topology,
            base=args.base,
        )
    except WriterLaneError as exc:
        print(str(exc))
        return 1

    print(f"WRITER_LANE_VALID:{identity}:{args.head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
