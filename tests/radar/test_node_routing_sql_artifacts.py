from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "supabase" / "migrations" / "20260906133630_radar_node_routing_hardening_v1.sql"
SQL_TEST = ROOT / "supabase" / "tests" / "radar_node_routing_hardening_v1.sql"


def test_node_routing_migration_is_forward_only_and_fail_closed():
    source = MIGRATION.read_text(encoding="utf-8").lower()

    assert "add column if not exists lease_expires_at timestamptz" in source
    assert "add column if not exists node_id uuid references radar.nodes" in source
    assert "having count(*) = 1" in source
    assert "set active = false" in source
    assert "not active or node_id is not null" in source
    assert "radar_subscription_node_identity_mismatch" in source
    assert "radar_node_identity_immutable" in source
    assert "before update of identity_id on radar.nodes" in source
    assert "lease_expires_at <= now()" in source
    assert "radar_invalid_stale_interval" in source
    assert "lease_expires_at = case" in source


def test_node_routing_migration_closes_client_function_execute_gap():
    source = MIGRATION.read_text(encoding="utf-8").lower()

    for signature in (
        "radar.assignment_ready(text)",
        "radar.mark_stale_nodes_offline(interval)",
        "radar.touch_node(uuid, text)",
        "radar.validate_subscription_node_identity()",
        "radar.prevent_node_identity_reassignment()",
    ):
        assert f"revoke all on function {signature} from public, anon, authenticated" in source


def test_node_routing_sql_test_covers_lease_and_identity_invariants():
    source = SQL_TEST.read_text(encoding="utf-8").lower()

    assert "radar_subscription_node_identity_mismatch" in source
    assert "radar_node_identity_immutable" in source
    assert "radar_active_subscription_node_required" in source
    assert "radar_stale_or_leaseless_node_remained_routable" in source
    assert "radar_invalid_stale_interval" in source
    assert "radar_touch_node_did_not_renew_lease" in source
    assert "radar_node_routing_function_execute_exposed" in source
    assert source.rstrip().endswith("rollback;")
