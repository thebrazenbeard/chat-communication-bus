#!/usr/bin/env python3
"""Run Radar's exception-oriented maintenance audit over a JSON state snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from radar.maintenance import audit


def _load(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("RADAR_AUDIT_STATE_MUST_BE_OBJECT")
    for key in ("required_lanes", "observed_lanes", "orphaned_identities"):
        if key in data and isinstance(data[key], list):
            data[key] = set(data[key]) if key != "orphaned_identities" else tuple(data[key])
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a Radar state snapshot and print material exceptions as JSON.")
    parser.add_argument("state", type=Path, help="JSON state snapshot")
    parser.add_argument("--fail-on-findings", action="store_true", help="exit 1 when findings exist")
    args = parser.parse_args(argv)

    findings = audit(_load(args.state))
    output = [{"code": item.code, "detail": item.detail} for item in findings]
    print(json.dumps(output, indent=2, sort_keys=True))
    return 1 if args.fail_on_findings and findings else 0


if __name__ == "__main__":
    sys.exit(main())
