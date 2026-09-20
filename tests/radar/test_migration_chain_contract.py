from pathlib import Path


EXPECTED_RADAR_MIGRATIONS = [
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
]


def test_radar_migration_versions_are_unique_and_provider_ordered() -> None:
    names = sorted(
        path.name
        for path in Path("supabase/migrations").glob("*_radar_*.sql")
    )
    assert names == EXPECTED_RADAR_MIGRATIONS
    assert len({name.split("_", 1)[0] for name in names}) == len(names)
