from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
ANCHOR_D = "401733b2013802880320629a4d8ea06f8bf7b760"
ANCHOR_D_TREE = "d3a9c44f0378409a626e29334b4d057ef20c7e8e"
ANCHOR_C = "f5ab21244a111b47708fa11e99d0e8ff7d8f5a45"


def test_dispatcher_trust_receipt_currentness_and_custody_agree_on_anchor_d() -> None:
    dispatcher = (ROOT / ".github/workflows/radar-central-dispatcher.yml").read_text(encoding="utf-8")
    trust = json.loads(
        (ROOT / "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V3.json").read_text(encoding="utf-8")
    )
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))
    custody = json.loads(
        (ROOT / "architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json").read_text(encoding="utf-8")
    )

    match = re.search(r"radar-trusted-projector\.yml@([0-9a-f]{40})", dispatcher)
    assert match is not None
    assert match.group(1) == ANCHOR_D
    assert trust["projection_anchor_sha"] == ANCHOR_D
    assert trust["projection_anchor_tree"] == ANCHOR_D_TREE
    assert trust["provider_expected_sha_value_at_deploy"] == ANCHOR_D
    assert current["projection_source"]["current_projection_anchor_d"] == ANCHOR_D
    assert current["projection_source"]["current_projection_anchor_d_tree"] == ANCHOR_D_TREE
    assert current["projection_trust_contract"] == "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V3.json"
    assert "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V3.json" in custody["paths"]


def test_anchor_c_is_historical_only_after_anchor_d_supersession() -> None:
    trust = json.loads(
        (ROOT / "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V3.json").read_text(encoding="utf-8")
    )
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))
    dispatcher = (ROOT / ".github/workflows/radar-central-dispatcher.yml").read_text(encoding="utf-8")

    assert trust["superseded_projection_anchor_sha"] == ANCHOR_C
    assert current["projection_source"]["historical_projection_anchor_c"] == ANCHOR_C
    assert ANCHOR_C not in dispatcher
    drift_codes = {item["code"] for item in current["known_provider_drift"]}
    assert "PROJECTION_ANCHOR_C_NOT_DEPLOYED" not in drift_codes
    assert "PROJECTION_ANCHOR_D_NOT_DEPLOYED" in drift_codes
    assert current["provider"]["projection_anchor_d_deployed"] is False


def test_anchor_d_is_frozen_reference_but_not_deployment_eligible_after_post_d_repairs() -> None:
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))
    source = current["projection_source"]

    assert source["current_projection_anchor_d"] == ANCHOR_D
    assert source["current_projection_anchor_d_deployment_eligible"] is False
    assert source["post_anchor_d_source_repairs_pending_successor_anchor"] is True
    assert source["successor_anchor_status"] == "PENDING_LOCAL_QUALIFICATION"

    drift = {item["code"]: item for item in current["known_provider_drift"]}
    defect = drift["PROJECTION_ANCHOR_D_KNOWN_PROTOCOL_DEFECT"]
    assert defect["severity"] == "HIGH"
    detail = defect["detail"]
    assert "project_batch" in detail
    assert "identity" in detail
    assert "branch" in detail
    assert "qualified successor" in detail.lower()
