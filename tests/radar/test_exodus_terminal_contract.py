from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_worker_runtime_contract_names_only_the_three_persistent_chat_interfaces():
    text = (ROOT / "docs" / "protocol" / "WORKER_RUNTIME_TERMINAL_V1.md").read_text(encoding="utf-8")
    required = {
        "`Vera`",
        "`Vera Control Plane Coordinator`",
        "`BT2 Coordinator`",
    }
    for name in required:
        assert name in text
    assert "No other worker, identity, reviewer, specialist, project lane, or coordinator requires a permanent ChatGPT conversation." in text


def test_radar_recovery_is_runtime_neutral_and_has_no_radar_chat_requirement():
    recovery = (ROOT / "docs" / "operator" / "RECOVERY.md").read_text(encoding="utf-8")
    assert "## Fresh operator/runtime terminal" in recovery
    assert "## Fresh ChatGPT session" not in recovery
    assert "requires no permanent Radar chat" in recovery


def test_stale_vera_lane_is_explicitly_superseded_by_topology():
    text = (ROOT / "docs" / "protocol" / "VERA_PROJECT_IDENTITY_AND_ATTUNEMENT_V1.md").read_text(encoding="utf-8")
    assert "ROUTE SUPERSEDED BY CURRENT TOPOLOGY" in text
    assert "`bus/vera-v2`" in text
    assert "Historical `bus/vera-sol-v1` remains provenance only" in text


def test_slack_relay_design_is_not_current_coordination_authority():
    text = (ROOT / "docs" / "SLACK_IDENTITY_RELAY.md").read_text(encoding="utf-8")
    assert "FUTURE_FRONTIER" in text
    assert "Slack is not the current system of record or an alternate worker coordination bus" in text
