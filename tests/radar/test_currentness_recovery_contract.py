from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CURRENT = ROOT / "architecture/contracts/RADAR_CURRENT.json"
SELF_REG = ROOT / "architecture/contracts/RADAR_SELF_REGISTRATION_V1.json"
ONBOARDING = ROOT / "architecture/contracts/RADAR_WRITER_LANE_ONBOARDING_V1.json"
SEED = ROOT / "supabase/seed/radar_v1.sql"
RECOVERY = ROOT / "docs/operator/RECOVERY.md"

EXPECTED_MIGRATIONS = [
    "20260902120716_radar_control_plane_v1.sql",
    "20260902120826_radar_realtime_v1.sql",
    "20260902203610_radar_visual_identity_v1.sql",
    "20260902204759_radar_live_message_projection_v1.sql",
    "20260902231445_radar_live_message_collision_v1.sql",
    "20260903000603_radar_receipt_plane_v1.sql",
    "20260903001906_radar_assignment_plane_v1.sql",
    "20260903113314_radar_operator_views_v1.sql",
    "20260903214334_radar_thread_closure_v1.sql",
    "20260905230823_radar_oidc_replay_guard_v1.sql",
    "20260906133630_radar_node_routing_hardening_v1.sql",
    "20260906154101_radar_projection_journal_v1.sql",
    "20260906165117_radar_projection_journal_api_v1.sql",
]


def test_current_contract_names_present_mailbox_and_full_source_chain() -> None:
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    assert current["current_mailbox_branch"] == "bus/radar-v2"
    assert current["source_migration_chain"] == EXPECTED_MIGRATIONS
    assert current["provider"]["applied_source_state"] == "PARTIAL_NOT_CURRENT"
    assert current["provider"]["projection_anchor_b_deployed"] is False
    assert current["provider"]["projection_journal_seeded"] is False
    assert current["provider"]["edge_body_bound_oidc_deployed"] is False
    assert current["known_provider_drift"]


def test_self_registration_and_current_seed_use_radar_v2_only() -> None:
    registration = json.loads(SELF_REG.read_text(encoding="utf-8"))
    assert registration["repository"]["mailbox_branch"] == "bus/radar-v2"
    seed = SEED.read_text(encoding="utf-8")
    assert "bus/radar-v2" in seed
    assert "bus/radar-v1" not in seed
    assert "radar/control-plane-v1" not in seed


def test_parallax_currentness_is_registered_inert_after_merged_topology() -> None:
    onboarding = json.loads(ONBOARDING.read_text(encoding="utf-8"))
    assert onboarding["topology_pr_merged"] is True
    assert onboarding["status"] == "FIRST_APPEND_PENDING"
    assert onboarding["lifecycle"] == "REGISTERED_INERT"
    assert onboarding["first_append_guard_verified"] is False
    assert onboarding["protected_effects"]["provider_projection"] is False


def test_recovery_uses_full_current_chain_and_never_replays_historical_topology_as_current() -> None:
    recovery = RECOVERY.read_text(encoding="utf-8")
    assert "every `supabase/tests/radar_*.sql`" in recovery
    assert "RADAR_SOURCE_CUSTODY_V1.json" in recovery
    assert "RADAR_TOPOLOGY_V1.json" in recovery
    assert "RADAR_WRITER_LANE_V2_CUTOVER.json" in recovery
    assert "historical evidence only" in recovery.lower()
    assert "do not apply historical writer-lane snapshots as current topology" in recovery.lower()
    assert "verify_jwt" in recovery
    assert "RADAR_TRUSTED_PROJECTOR_SHA" in recovery
    assert "projection cursor" in recovery.lower()
