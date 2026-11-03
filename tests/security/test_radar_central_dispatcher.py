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
    top_level_keys = []
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        if line[0] not in " \t":
            # Reject duplicate/quoted event keys, YAML merge keys, and any
            # unexpected top-level construct instead of interpreting YAML 1.1.
            match = re.match(r"^([a-z_]+):", line)
            assert match is not None, line
            top_level_keys.append(match.group(1))

    assert top_level_keys == ["name", "on", "permissions", "jobs"]
    assert "on:" in lines
    assert "permissions:" in lines
    event_start = lines.index("on:") + 1
    event_end = lines.index("permissions:")
    event_block = [line for line in lines[event_start:event_end] if line.strip() and not line.lstrip().startswith("#")]
    # Exact whitelist: aliases, anchors, merges and extra trigger events fail.
    assert event_block == ["  workflow_dispatch:"], event_block


def test_dispatcher_remains_manual_only_during_public_transition_hold() -> None:
    _assert_public_transition_manual_hold(DISPATCHER.read_text(encoding="utf-8"))


def test_public_transition_hold_detects_synthetic_automatic_triggers() -> None:
    source = DISPATCHER.read_text(encoding="utf-8")
    assert source.count("  workflow_dispatch:\n") == 1
    mutants = [
        source.replace(
            "  workflow_dispatch:\n", f"  {trigger}:\n  workflow_dispatch:\n", 1
        )
        for trigger in ("schedule", "workflow_run", "push", "repository_dispatch")
    ]
    mutants += [
        source + '\n"on":\n  schedule:\n    - cron: "*/5 * * * *"\n',
        source + "\n'on':\n  workflow_run:\n",
        source + "\n<<: *events\n",
        source.replace("on:\n", "on: *events\n", 1),
        source.replace("  workflow_dispatch:\n", "  <<: *events\n  workflow_dispatch:\n", 1),
    ]
    for unsafe in mutants:
        try:
            _assert_public_transition_manual_hold(unsafe)
        except AssertionError:
            continue
        raise AssertionError("Unsafe event/alias/duplicate-key mutant escaped public-transition test")


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
