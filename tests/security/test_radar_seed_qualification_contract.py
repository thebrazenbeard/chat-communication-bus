from __future__ import annotations

import json
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]
SUPABASE_CONFIG = ROOT / "supabase/config.toml"
CUSTODY = ROOT / "architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json"
SEED = ROOT / "supabase/seed/radar_v1.sql"
POST_SEED_ASSERTION = ROOT / "supabase/tests/radar_self_registration_seed_v1.sql"
STABLE_NODE_ID = "72616461-722d-4000-8000-000000000001"
EXPECTED_DOMAINS = {
    "coordination",
    "system",
    "security",
    "database",
    "repository",
    "protocol",
}


def test_local_reset_executes_current_radar_recovery_seed() -> None:
    config = tomllib.loads(SUPABASE_CONFIG.read_text(encoding="utf-8"))
    assert config["db"]["seed"] == {
        "enabled": True,
        "sql_paths": ["./seed/radar_v1.sql"],
    }


def test_source_custody_v17_binds_recovery_seed_and_registration_contract() -> None:
    custody = json.loads(CUSTODY.read_text(encoding="utf-8"))
    assert custody["version"] == 17
    paths = set(custody["paths"])
    assert "supabase/seed/radar_v1.sql" in paths
    assert "architecture/contracts/RADAR_SELF_REGISTRATION_V1.json" in paths


def test_post_seed_sql_assertion_proves_reset_state_before_replay_and_idempotence_after() -> None:
    assert POST_SEED_ASSERTION.exists()
    source = POST_SEED_ASSERTION.read_text(encoding="utf-8")
    replay_marker = r"\ir ../seed/radar_v1.sql"

    assert replay_marker in source
    before_replay, after_replay = source.split(replay_marker, 1)
    assert "RADAR_SEED_PRE_REPLAY_STABLE_NODE_INVALID" in before_replay
    assert "RADAR_SEED_PRE_REPLAY_MAILBOX_INVALID" in before_replay
    assert "RADAR_SEED_PRE_REPLAY_SUBSCRIPTIONS_INVALID" in before_replay

    assert STABLE_NODE_ID in before_replay
    assert "OFFLINE" in before_replay
    assert "last_heartbeat is null" in before_replay.lower()
    assert "lease_expires_at is null" in before_replay.lower()
    assert "radar-github-mailbox" in before_replay
    assert "bus/radar-v2" in before_replay
    for domain in EXPECTED_DOMAINS:
        assert f"'{domain}'" in before_replay

    assert STABLE_NODE_ID in after_replay
    assert "RADAR_SEED_POST_REPLAY_STABLE_NODE_INVALID" in after_replay
    assert "RADAR_SEED_POST_REPLAY_MAILBOX_INVALID" in after_replay
    assert "RADAR_SEED_POST_REPLAY_SUBSCRIPTIONS_INVALID" in after_replay
    assert "RADAR_SEED_POST_REPLAY_UNEXPECTED_ACTIVE_SUBSCRIPTIONS" in after_replay
    assert "node_id is null" in after_replay.lower()
    assert "count(*)" in source.lower()
