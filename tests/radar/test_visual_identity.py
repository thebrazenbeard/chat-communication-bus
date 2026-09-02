from pathlib import Path

import pytest

from radar.visual_identity import (
    VisualIdentityError,
    load_visual_profile,
    resolve_bus_avatar,
    validate_visual_profile,
)


def base_profile():
    return {
        "identity_id": "radar",
        "display_name": "Radar",
        "style_contract": "BUS_AVATAR_STYLE_V1",
        "current": {"portrait": "radar-portrait-v1"},
        "active_candidate": {},
        "assets": [
            {
                "asset_id": "radar-portrait-v1",
                "scope": "portrait",
                "state": "CANONICAL",
                "path": "identities/radar/assets/radar.png",
                "sha256": "a" * 64,
                "claimed_by": "radar",
                "claim_type": "self",
                "claimed_at": "2026-09-02T00:00:00Z",
                "source_ref": "self-claim:test",
            }
        ],
    }


def test_valid_self_canonical_profile():
    profile = validate_visual_profile(base_profile())
    assert profile.identity_id == "radar"
    assert profile.assets[0].claim_type == "self"
    assert profile.assets[0].state == "CANONICAL"


def test_identity_path_mismatch_fails():
    data = base_profile()
    data["assets"][0]["path"] = "identities/vera/assets/radar.png"
    with pytest.raises(VisualIdentityError, match="ASSET_PATH_IDENTITY_MISMATCH"):
        validate_visual_profile(data)


def test_duplicate_current_canonical_scope_fails():
    data = base_profile()
    second = dict(data["assets"][0])
    second["asset_id"] = "radar-portrait-v2"
    second["path"] = "identities/radar/assets/radar2.png"
    second["sha256"] = "b" * 64
    data["assets"].append(second)
    with pytest.raises(VisualIdentityError, match="MULTIPLE_CANONICAL_ASSETS_FOR_SCOPE"):
        validate_visual_profile(data)


def test_active_candidate_must_point_to_candidate_same_scope():
    data = base_profile()
    data["active_candidate"] = {"portrait": "radar-portrait-v1"}
    with pytest.raises(VisualIdentityError, match="ACTIVE_CANDIDATE_INVALID"):
        validate_visual_profile(data)


def test_current_pointer_cannot_target_retired_asset():
    data = base_profile()
    data["assets"][0]["state"] = "RETIRED"
    data["assets"][0]["retired_at"] = "2026-09-02T01:00:00Z"
    with pytest.raises(VisualIdentityError, match="CURRENT_ASSET_INVALID"):
        validate_visual_profile(data)


def test_malformed_sha256_fails():
    data = base_profile()
    data["assets"][0]["sha256"] = "not-a-digest"
    with pytest.raises(VisualIdentityError, match="INVALID_SHA256"):
        validate_visual_profile(data)


def test_bus_avatar_candidate_requires_explicit_policy():
    data = base_profile()
    data["assets"].append(
        {
            "asset_id": "radar-avatar-candidate-v1",
            "scope": "bus_avatar",
            "state": "CANDIDATE",
            "path": "identities/radar/assets/avatar.png",
            "sha256": "b" * 64,
            "claimed_by": "radar",
            "claim_type": "self",
            "claimed_at": "2026-09-02T00:00:00Z",
            "source_ref": "self-claim:test-avatar",
        }
    )
    data["active_candidate"] = {"bus_avatar": "radar-avatar-candidate-v1"}
    profile = validate_visual_profile(data)
    assert resolve_bus_avatar(profile) is None
    candidate = resolve_bus_avatar(profile, allow_candidate=True)
    assert candidate.asset_id == "radar-avatar-candidate-v1"
    assert candidate.state == "CANDIDATE"


def test_canonical_bus_avatar_wins_over_candidate():
    data = base_profile()
    data["assets"].extend(
        [
            {
                "asset_id": "radar-avatar-canon-v1",
                "scope": "bus_avatar",
                "state": "CANONICAL",
                "path": "identities/radar/assets/avatar-canon.png",
                "sha256": "b" * 64,
                "claimed_by": "radar",
                "claim_type": "self",
                "claimed_at": "2026-09-02T00:00:00Z",
                "source_ref": "self-claim:test-avatar-canon",
            },
            {
                "asset_id": "radar-avatar-candidate-v2",
                "scope": "bus_avatar",
                "state": "CANDIDATE",
                "path": "identities/radar/assets/avatar-candidate.png",
                "sha256": "c" * 64,
                "claimed_by": "radar",
                "claim_type": "self",
                "claimed_at": "2026-09-02T00:00:00Z",
                "source_ref": "self-claim:test-avatar-candidate",
            },
        ]
    )
    data["current"]["bus_avatar"] = "radar-avatar-canon-v1"
    data["active_candidate"] = {"bus_avatar": "radar-avatar-candidate-v2"}
    profile = validate_visual_profile(data)
    assert resolve_bus_avatar(profile, allow_candidate=True).asset_id == "radar-avatar-canon-v1"


def test_repository_radar_profile_exists_but_does_not_forge_uncustodied_asset():
    root = Path(__file__).resolve().parents[2]
    profile = load_visual_profile(root / "identities" / "radar" / "profile.json")
    assert profile.identity_id == "radar"
    assert profile.style_contract == "BUS_AVATAR_STYLE_V1"
    assert profile.current == {}
    assert profile.active_candidate == {}
    assert profile.assets == ()
    assert resolve_bus_avatar(profile) is None
