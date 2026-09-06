from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANCHOR_B = "7076c73595d5a572e0f374c3a495b29982d92bed"
ANCHOR_C = "f5ab21244a111b47708fa11e99d0e8ff7d8f5a45"


def test_anchor_c_receipt_preserves_b_to_c_historical_lineage() -> None:
    trust_c = json.loads(
        (ROOT / "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V2.json").read_text(encoding="utf-8")
    )
    trust_d = json.loads(
        (ROOT / "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V3.json").read_text(encoding="utf-8")
    )

    assert trust_c["projection_anchor_sha"] == ANCHOR_C
    assert trust_c["superseded_projection_anchor_sha"] == ANCHOR_B
    assert trust_d["superseded_projection_anchor_sha"] == ANCHOR_C
    assert trust_d["supersedes_source_anchor_contract"] == "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V2.json"
