from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANCHOR_D = "401733b2013802880320629a4d8ea06f8bf7b760"
ANCHOR_D_TREE = "d3a9c44f0378409a626e29334b4d057ef20c7e8e"
ANCHOR_C = "f5ab21244a111b47708fa11e99d0e8ff7d8f5a45"
ANCHOR_E = "dfd3c639d058dcafaa1167e53ad4bdc152d52cf6"


def test_anchor_d_contract_remains_immutable_historical_evidence() -> None:
    trust_d = json.loads(
        (ROOT / "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V3.json").read_text(encoding="utf-8")
    )
    trust_e = json.loads(
        (ROOT / "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V4.json").read_text(encoding="utf-8")
    )
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))
    custody = json.loads(
        (ROOT / "architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json").read_text(encoding="utf-8")
    )

    assert trust_d["projection_anchor_sha"] == ANCHOR_D
    assert trust_d["projection_anchor_tree"] == ANCHOR_D_TREE
    assert trust_d["superseded_projection_anchor_sha"] == ANCHOR_C
    assert trust_e["superseded_projection_anchor_sha"] == ANCHOR_D
    assert current["projection_source"]["historical_projection_anchor_d"] == ANCHOR_D
    assert current["projection_source"]["historical_projection_anchor_d_tree"] == ANCHOR_D_TREE
    assert "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V3.json" in custody["paths"]


def test_anchor_d_is_not_current_or_deployment_target_after_anchor_e_freeze() -> None:
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))
    dispatcher = (ROOT / ".github/workflows/radar-central-dispatcher.yml").read_text(encoding="utf-8")

    source = current["projection_source"]
    assert source["current_projection_anchor_e"] == ANCHOR_E
    assert source["current_projection_anchor_e_deployment_eligible"] is True
    assert source["post_anchor_d_source_repairs_pending_successor_anchor"] is False
    assert source["successor_anchor_status"] == "FROZEN_QUALIFIED_SOURCE_ONLY"
    assert ANCHOR_E in dispatcher
    assert ANCHOR_D not in dispatcher
    assert current["provider"]["projection_anchor_d_deployed"] is False
    assert current["provider"]["projection_anchor_e_deployed"] is False

    drift_codes = {item["code"] for item in current["known_provider_drift"]}
    assert "PROJECTION_ANCHOR_D_KNOWN_PROTOCOL_DEFECT" not in drift_codes
    assert "PROJECTION_ANCHOR_D_KNOWN_ATOMICITY_DEFECT" not in drift_codes
    assert "PROJECTION_ANCHOR_E_NOT_DEPLOYED" in drift_codes
