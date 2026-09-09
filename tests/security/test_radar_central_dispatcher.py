from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / ".github" / "workflows" / "radar-central-dispatcher.yml"
VALIDATE_ANCHOR = ROOT / "architecture" / "contracts" / "RADAR_TRUST_ANCHOR_V1.json"
PROJECTION_ANCHOR = ROOT / "architecture" / "contracts" / "RADAR_PROJECTION_TRUST_ANCHOR_V4.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def test_dispatcher_has_workflow_run_wakeup_and_five_minute_backstop() -> None:
    source = DISPATCHER.read_text(encoding="utf-8")
    assert 'workflows: ["Writer Lane Guard"]' in source
    assert "types: [completed]" in source
    assert 'branches: ["bus/**"]' in source
    assert 'cron: "*/5 * * * *"' in source
    assert "workflow_dispatch:" not in source


def test_dispatcher_pins_exact_projection_anchor_and_passes_no_authority_inputs() -> None:
    source = DISPATCHER.read_text(encoding="utf-8")
    contract = json.loads(PROJECTION_ANCHOR.read_text(encoding="utf-8"))
    anchor = contract["projection_anchor_sha"]
    assert FULL_SHA.fullmatch(anchor)

    expected = (
        "uses: thebrazenbeard/chat-communication-bus/.github/workflows/"
        f"radar-trusted-projector.yml@{anchor}"
    )
    assert expected in source
    assert "runs-on:" not in source
    assert "with:" not in source
    assert "secrets:" not in source
    assert "github.event.workflow_run.head_sha" not in source
    assert "github.event.workflow_run.head_branch" not in source
    assert "if:" not in source


def test_projection_anchor_receipt_preserves_source_only_provider_ceiling() -> None:
    contract = json.loads(PROJECTION_ANCHOR.read_text(encoding="utf-8"))
    assert contract["status"] == "SOURCE_ONLY_NOT_ACTIVE"
    assert contract["deployment_eligible_source"] is True
    assert contract["qualification_receipt_status"] == "ADMITTED_PASS"
    assert contract["provider_trust_status"] == "NOT_DEPLOYED"
    assert contract["journal_provider_status"] == "NOT_MIGRATED"
    assert contract["cursor_seed_status"] == "NOT_SEEDED"
    assert contract["dispatcher_status"] == "SOURCE_ONLY_NOT_ACTIVE"
    assert contract["provider_expected_sha_value_at_deploy"] == contract["projection_anchor_sha"]
    assert contract["reusable_workflow_path"] == ".github/workflows/radar-trusted-projector.yml"


def test_validate_only_anchor_a_remains_historical_and_distinct_from_current_projection_anchor() -> None:
    a = json.loads(VALIDATE_ANCHOR.read_text(encoding="utf-8"))
    current = json.loads(PROJECTION_ANCHOR.read_text(encoding="utf-8"))
    assert a["trust_anchor_sha"] != current["projection_anchor_sha"]
    assert a["provider_trust_status"] == "NOT_UPDATED_FOR_A"
