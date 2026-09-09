from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
ANCHOR_E = "dfd3c639d058dcafaa1167e53ad4bdc152d52cf6"
ANCHOR_E_TREE = "8e51a28db92739d2ce103c72194330dc84a7c415"
ANCHOR_D = "401733b2013802880320629a4d8ea06f8bf7b760"


def test_dispatcher_trust_currentness_and_custody_agree_on_qualified_anchor_e() -> None:
    dispatcher = (ROOT / ".github/workflows/radar-central-dispatcher.yml").read_text(encoding="utf-8")
    trust = json.loads(
        (ROOT / "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V4.json").read_text(encoding="utf-8")
    )
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))
    custody = json.loads(
        (ROOT / "architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json").read_text(encoding="utf-8")
    )

    match = re.search(r"radar-trusted-projector\.yml@([0-9a-f]{40})", dispatcher)
    assert match is not None
    assert match.group(1) == ANCHOR_E
    assert trust["projection_anchor_sha"] == ANCHOR_E
    assert trust["projection_anchor_tree"] == ANCHOR_E_TREE
    assert trust["provider_expected_sha_value_at_deploy"] == ANCHOR_E
    assert trust["qualified_source_commit"] == ANCHOR_E
    assert trust["qualified_source_tree"] == ANCHOR_E_TREE
    assert trust["qualification_receipt_status"] == "ADMITTED_PASS"
    assert current["projection_source"]["current_projection_anchor_e"] == ANCHOR_E
    assert current["projection_source"]["current_projection_anchor_e_tree"] == ANCHOR_E_TREE
    assert current["projection_source"]["current_projection_anchor_e_deployment_eligible"] is True
    assert current["projection_source"]["successor_anchor_status"] == "FROZEN_QUALIFIED_SOURCE_ONLY"
    assert current["projection_trust_contract"] == "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V4.json"
    assert "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V4.json" in custody["paths"]


def test_anchor_d_is_historical_and_explicitly_not_deployment_eligible_after_anchor_e_freeze() -> None:
    trust = json.loads(
        (ROOT / "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V4.json").read_text(encoding="utf-8")
    )
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))
    dispatcher = (ROOT / ".github/workflows/radar-central-dispatcher.yml").read_text(encoding="utf-8")

    assert trust["superseded_projection_anchor_sha"] == ANCHOR_D
    assert current["projection_source"]["historical_projection_anchor_d"] == ANCHOR_D
    assert ANCHOR_D not in dispatcher
    assert current["provider"]["projection_anchor_e_deployed"] is False
    assert current["projection_source"]["post_anchor_d_source_repairs_pending_successor_anchor"] is False

    drift_codes = {item["code"] for item in current["known_provider_drift"]}
    assert "PROJECTION_ANCHOR_D_KNOWN_PROTOCOL_DEFECT" not in drift_codes
    assert "PROJECTION_ANCHOR_D_KNOWN_ATOMICITY_DEFECT" not in drift_codes
    assert "PROJECTION_ANCHOR_E_NOT_DEPLOYED" in drift_codes
