from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
ANCHOR_C = "f5ab21244a111b47708fa11e99d0e8ff7d8f5a45"
ANCHOR_B = "7076c73595d5a572e0f374c3a495b29982d92bed"


def test_dispatcher_trust_receipt_and_currentness_agree_on_anchor_c() -> None:
    dispatcher = (ROOT / ".github/workflows/radar-central-dispatcher.yml").read_text(encoding="utf-8")
    trust = json.loads(
        (ROOT / "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V2.json").read_text(encoding="utf-8")
    )
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))

    match = re.search(
        r"radar-trusted-projector\.yml@([0-9a-f]{40})",
        dispatcher,
    )
    assert match is not None
    assert match.group(1) == ANCHOR_C
    assert trust["projection_anchor_sha"] == ANCHOR_C
    assert trust["provider_expected_sha_value_at_deploy"] == ANCHOR_C
    assert current["projection_source"]["current_projection_anchor_c"] == ANCHOR_C
    assert current["projection_trust_contract"] == "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V2.json"


def test_anchor_b_is_historical_only_after_anchor_c_supersession() -> None:
    trust = json.loads(
        (ROOT / "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V2.json").read_text(encoding="utf-8")
    )
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))
    dispatcher = (ROOT / ".github/workflows/radar-central-dispatcher.yml").read_text(encoding="utf-8")

    assert trust["superseded_projection_anchor_sha"] == ANCHOR_B
    assert current["projection_source"]["historical_projection_anchor_b"] == ANCHOR_B
    assert ANCHOR_B not in dispatcher
    assert "PROJECTION_ANCHOR_B_NOT_DEPLOYED" not in {
        item["code"] for item in current["known_provider_drift"]
    }
    assert "PROJECTION_ANCHOR_C_NOT_DEPLOYED" in {
        item["code"] for item in current["known_provider_drift"]
    }
