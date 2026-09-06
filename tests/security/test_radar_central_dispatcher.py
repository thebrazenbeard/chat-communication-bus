from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / ".github" / "workflows" / "radar-central-dispatcher.yml"
ANCHOR = ROOT / "architecture" / "contracts" / "RADAR_TRUST_ANCHOR_V1.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def test_dispatcher_has_workflow_run_wakeup_and_five_minute_backstop() -> None:
    source = DISPATCHER.read_text(encoding="utf-8")
    assert 'workflows: ["Writer Lane Guard"]' in source
    assert "types: [completed]" in source
    assert 'branches: ["bus/**"]' in source
    assert 'cron: "*/5 * * * *"' in source
    assert "workflow_dispatch:" not in source


def test_dispatcher_pins_exact_trust_anchor_and_passes_no_authority_inputs() -> None:
    source = DISPATCHER.read_text(encoding="utf-8")
    contract = json.loads(ANCHOR.read_text(encoding="utf-8"))
    anchor = contract["trust_anchor_sha"]
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


def test_trust_anchor_receipt_preserves_source_only_ceiling() -> None:
    contract = json.loads(ANCHOR.read_text(encoding="utf-8"))
    assert contract["status"] == "SOURCE_ONLY_NOT_ACTIVE"
    assert contract["provider_trust_status"] == "NOT_UPDATED_FOR_A"
    assert contract["dispatcher_status"] == "SOURCE_ONLY_NOT_ACTIVE"
    assert contract["reusable_workflow_path"] == ".github/workflows/radar-trusted-projector.yml"
