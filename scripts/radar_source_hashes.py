#!/usr/bin/env python3
"""Emit SHA-256 and byte length for Git-bound Radar provider source files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "supabase/migrations/20260902120716_radar_control_plane_v1.sql",
    "supabase/migrations/20260902120826_radar_realtime_v1.sql",
    "supabase/seed/radar_v1.sql",
)


def source_receipts() -> list[dict[str, object]]:
    receipts: list[dict[str, object]] = []
    for relative in FILES:
        path = ROOT / relative
        data = path.read_bytes()
        receipts.append(
            {
                "path": relative,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return receipts


if __name__ == "__main__":
    print(json.dumps(source_receipts(), sort_keys=True))
