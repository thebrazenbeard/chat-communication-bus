#!/usr/bin/env python3
"""Emit SHA-256 and byte length for every source bound by Radar custody."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json"


class SourceCustodyError(RuntimeError):
    pass


def _load_manifest() -> dict[str, object]:
    try:
        raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceCustodyError("SOURCE_CUSTODY_MANIFEST_INVALID") from exc
    if not isinstance(raw, dict) or raw.get("contract") != "RADAR_SOURCE_CUSTODY_V1":
        raise SourceCustodyError("SOURCE_CUSTODY_MANIFEST_INVALID")
    return raw


def custody_paths() -> tuple[str, ...]:
    contract = _load_manifest()
    fixed = contract.get("paths")
    globs = contract.get("required_globs")
    if not isinstance(fixed, list) or not all(isinstance(item, str) and item for item in fixed):
        raise SourceCustodyError("SOURCE_CUSTODY_PATHS_INVALID")
    if not isinstance(globs, list) or not all(isinstance(item, str) and item for item in globs):
        raise SourceCustodyError("SOURCE_CUSTODY_GLOBS_INVALID")

    selected = set(fixed)
    for pattern in globs:
        matches = sorted(
            path.relative_to(ROOT).as_posix()
            for path in ROOT.glob(pattern)
            if path.is_file()
        )
        if not matches:
            raise SourceCustodyError(f"SOURCE_CUSTODY_GLOB_EMPTY:{pattern}")
        selected.update(matches)

    for relative in sorted(selected):
        path = ROOT / relative
        if not path.is_file():
            raise SourceCustodyError(f"SOURCE_CUSTODY_PATH_MISSING:{relative}")
    return tuple(sorted(selected))


def source_receipts() -> list[dict[str, object]]:
    receipts: list[dict[str, object]] = []
    for relative in custody_paths():
        data = (ROOT / relative).read_bytes()
        receipts.append(
            {
                "path": relative,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return receipts


if __name__ == "__main__":
    print(json.dumps(source_receipts(), sort_keys=True, separators=(",", ":")))
