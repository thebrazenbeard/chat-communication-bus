from pathlib import Path

from radar.visual_identity import validate_visual_profile
from radar.visual_projection import build_visual_projection_commands, visual_asset_row


def profile_with_assets():
    return validate_visual_profile(
        {
            "identity_id": "radar",
            "display_name": "Radar",
            "style_contract": "BUS_AVATAR_STYLE_V1",
            "current": {"portrait": "portrait-v1"},
            "active_candidate": {"bus_avatar": "avatar-c1"},
            "assets": [
                {
                    "asset_id": "portrait-v1",
                    "scope": "portrait",
                    "state": "CANONICAL",
                    "path": "identities/radar/assets/portrait.png",
                    "sha256": "a" * 64,
                    "claimed_by": "radar",
                    "claim_type": "self",
                    "claimed_at": "2026-09-02T00:00:00Z",
                    "source_ref": "claim:portrait",
                },
                {
                    "asset_id": "avatar-c1",
                    "scope": "bus_avatar",
                    "state": "CANDIDATE",
                    "path": "identities/radar/assets/avatar.png",
                    "sha256": "b" * 64,
                    "claimed_by": "radar",
                    "claim_type": "self",
                    "claimed_at": "2026-09-02T00:01:00Z",
                    "source_ref": "claim:avatar",
                    "review_after": "2026-10-01T00:00:00Z",
                },
            ],
        }
    )


def test_visual_asset_row_is_metadata_only_and_preserves_state():
    profile = profile_with_assets()
    row = visual_asset_row(profile, profile.assets[1])
    assert row["identity_id"] == "radar"
    assert row["asset_id"] == "avatar-c1"
    assert row["scope"] == "bus_avatar"
    assert row["state"] == "CANDIDATE"
    assert row["style_contract"] == "BUS_AVATAR_STYLE_V1"
    assert row["is_active_candidate"] is True
    assert row["is_current"] is False
    assert "bytes" not in row
    assert "blob" not in row
    assert "body" not in row


def test_projection_commands_are_stable_upserts_without_image_payloads():
    commands = build_visual_projection_commands(profile_with_assets())
    assert len(commands) == 2
    assert {command.operation for command in commands} == {"UPSERT_IDENTITY_VISUAL"}
    for command in commands:
        assert command.schema == "radar"
        assert "radar.identity_visuals" in command.sql
        assert "on conflict (asset_id)" in command.sql
        lowered = command.sql.lower()
        assert "bytea" not in lowered
        assert "image_bytes" not in lowered
        assert all(not isinstance(value, (bytes, bytearray)) for value in command.parameters.values())


def test_migration_contract_has_metadata_table_rls_and_no_binary_column():
    root = Path(__file__).resolve().parents[2]
    sql = (root / "supabase" / "migrations" / "20260902203610_radar_visual_identity_v1.sql").read_text()
    lowered = sql.lower()
    assert "create table if not exists radar.identity_visuals" in lowered
    assert "enable row level security" in lowered
    assert "references radar.identities(identity_id)" in lowered
    assert "bytea" not in lowered
    assert "image_bytes" not in lowered
