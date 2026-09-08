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


def test_post_seed_sql_assertion_replays_seed_and_checks_recovery_state() -> None:
    assert POST_SEED_ASSERTION.exists()
    source = POST_SEED_ASSERTION.read_text(encoding="utf-8")

    assert r"\ir ../seed/radar_v1.sql" in source
    assert STABLE_NODE_ID in source
    assert "OFFLINE" in source
    assert "last_heartbeat is null" in source.lower()
    assert "lease_expires_at is null" in source.lower()
    assert "radar-github-mailbox" in source
    assert "bus/radar-v2" in source

    for domain in EXPECTED_DOMAINS:
        assert f"'{domain}'" in source

    assert "node_id is null" in source.lower()
    assert "count(*)" in source.lower()
