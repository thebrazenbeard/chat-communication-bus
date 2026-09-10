#!/usr/bin/env python3
"""Emit a deterministic read-only snapshot of the configured GitHub Project queue."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from radar.project_queue import (  # noqa: E402
    ProjectQueueError,
    ProjectQueueReader,
    load_project_queue_spec,
    render_snapshot_json,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        default=str(ROOT / "architecture/contracts/RADAR_PROJECT_QUEUE_V1.json"),
    )
    args = parser.parse_args()

    spec = load_project_queue_spec(args.contract)
    snapshot = ProjectQueueReader(spec).read()
    sys.stdout.write(render_snapshot_json(snapshot))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProjectQueueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
