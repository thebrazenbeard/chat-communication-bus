from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / ".github" / "workflows" / "radar-central-dispatcher.yml"
VALIDATE_ANCHOR = ROOT / "architecture" / "contracts" / "RADAR_TRUST_ANCHOR_V1.json"
PROJECTION_ANCHOR = ROOT / "architecture" / "contracts" / "RADAR_PROJECTION_TRUST_ANCHOR_V4.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def _assert_public_transition_manual_hold(source: str) -> None:
    """Fail closed if any automatic trigger returns to the public Bus."""
    assert "# PUBLIC TRANSITION HOLD" in source

    lines = source.splitlines()
    assert sum(line.startswith("on:") for line in lines) == 1
    assert "on:" in lines  # Reject inline YAML event declarations.

    event_lines = []
    in_events = False
    for line in lines:
        if line == "on:":
            in_events = True
            continue
        if not in_events:
            continue
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] not in " \t":
            break
        match = re.match(r"^  ([a-z_][a-z_0-9]*):(?:[ \t]|$)", line)
        if match:
            event_lines.append(match.group(1))

    assert event_lines == ["workflow_dispatch"], event_lines


def test_dispatcher_remains_manual_only_during_public_transition_hold() -> None:
    _assert_public_transition_manual_hold(DISPATCHER.read_text(encoding="utf-8"))


def test_public_transition_hold_detects_synthetic_automatic_triggers() -> None:
    source = DISPATCHER.read_text(encoding="utf-8")
    assert source.count("  workflow_dispatch:\n") == 1
    for trigger in ("schedule", "workflow_run", "push", "repository_dispatch"):
        unsafe = source.replace(
            "  workflow_dispatch:\n", f"  {trigger}:\n  workflow_dispatch:\n", 1
        )
        try:
            _assert_public_transition_manual_hold(unsafe)
        except AssertionError:
            continue
        raise AssertionError(f"Unsafe {trigger} event escaped public-transition test")


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
