from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


class VisualIdentityError(ValueError):
    """Raised when repository visual identity evidence is invalid."""


_ALLOWED_SCOPES = {"portrait", "bus_avatar", "character"}
_ALLOWED_STATES = {"PLACEHOLDER", "CANDIDATE", "CANONICAL", "RETIRED"}
_ALLOWED_CLAIM_TYPES = {"self", "operator_override", "system_placeholder"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class VisualAsset:
    asset_id: str
    scope: str
    state: str
    path: str
    sha256: str
    claimed_by: str
    claim_type: str
    claimed_at: str
    source_ref: str
    supersedes: str | None = None
    retired_at: str | None = None
    review_after: str | None = None


@dataclass(frozen=True)
class VisualProfile:
    identity_id: str
    display_name: str
    style_contract: str
    current: dict[str, str]
    active_candidate: dict[str, str]
    assets: tuple[VisualAsset, ...]


def _required_string(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise VisualIdentityError(f"MISSING_OR_INVALID_{key.upper()}")
    return value


def _parse_asset(identity_id: str, record: Mapping[str, Any]) -> VisualAsset:
    asset_id = _required_string(record, "asset_id")
    scope = _required_string(record, "scope")
    state = _required_string(record, "state")
    path = _required_string(record, "path")
    sha256 = _required_string(record, "sha256")
    claimed_by = _required_string(record, "claimed_by")
    claim_type = _required_string(record, "claim_type")
    claimed_at = _required_string(record, "claimed_at")
    source_ref = _required_string(record, "source_ref")

    if scope not in _ALLOWED_SCOPES:
        raise VisualIdentityError("UNKNOWN_VISUAL_SCOPE")
    if state not in _ALLOWED_STATES:
        raise VisualIdentityError("UNKNOWN_VISUAL_STATE")
    if claim_type not in _ALLOWED_CLAIM_TYPES:
        raise VisualIdentityError("UNKNOWN_CLAIM_TYPE")
    if not _SHA256_RE.fullmatch(sha256):
        raise VisualIdentityError("INVALID_SHA256")

    asset_path = PurePosixPath(path)
    expected_prefix = PurePosixPath("identities") / identity_id / "assets"
    if asset_path.is_absolute() or ".." in asset_path.parts:
        raise VisualIdentityError("ASSET_PATH_IDENTITY_MISMATCH")
    if asset_path.parts[: len(expected_prefix.parts)] != expected_prefix.parts:
        raise VisualIdentityError("ASSET_PATH_IDENTITY_MISMATCH")
    if len(asset_path.parts) <= len(expected_prefix.parts):
        raise VisualIdentityError("ASSET_PATH_IDENTITY_MISMATCH")

    retired_at = record.get("retired_at")
    if state == "RETIRED" and (not isinstance(retired_at, str) or not retired_at.strip()):
        raise VisualIdentityError("RETIRED_ASSET_MISSING_RETIRED_AT")

    return VisualAsset(
        asset_id=asset_id,
        scope=scope,
        state=state,
        path=path,
        sha256=sha256,
        claimed_by=claimed_by,
        claim_type=claim_type,
        claimed_at=claimed_at,
        source_ref=source_ref,
        supersedes=record.get("supersedes"),
        retired_at=retired_at,
        review_after=record.get("review_after"),
    )


def validate_visual_profile(data: Mapping[str, Any] | VisualProfile) -> VisualProfile:
    if isinstance(data, VisualProfile):
        profile = data
    else:
        identity_id = _required_string(data, "identity_id")
        display_name = _required_string(data, "display_name")
        style_contract = _required_string(data, "style_contract")
        if style_contract != "BUS_AVATAR_STYLE_V1":
            raise VisualIdentityError("UNKNOWN_STYLE_CONTRACT")

        raw_assets = data.get("assets", [])
        if not isinstance(raw_assets, list):
            raise VisualIdentityError("INVALID_ASSET_LIST")
        assets = tuple(_parse_asset(identity_id, record) for record in raw_assets)

        raw_current = data.get("current", {})
        raw_candidate = data.get("active_candidate", {})
        if not isinstance(raw_current, dict) or not isinstance(raw_candidate, dict):
            raise VisualIdentityError("INVALID_CURRENT_POINTERS")

        profile = VisualProfile(
            identity_id=identity_id,
            display_name=display_name,
            style_contract=style_contract,
            current=dict(raw_current),
            active_candidate=dict(raw_candidate),
            assets=assets,
        )

    by_id: dict[str, VisualAsset] = {}
    canonical_by_scope: dict[str, list[VisualAsset]] = {}
    for asset in profile.assets:
        if asset.asset_id in by_id:
            raise VisualIdentityError("DUPLICATE_ASSET_ID")
        by_id[asset.asset_id] = asset
        if asset.state == "CANONICAL":
            canonical_by_scope.setdefault(asset.scope, []).append(asset)

    if any(len(items) > 1 for items in canonical_by_scope.values()):
        raise VisualIdentityError("MULTIPLE_CANONICAL_ASSETS_FOR_SCOPE")

    for scope, asset_id in profile.current.items():
        if scope not in _ALLOWED_SCOPES or not isinstance(asset_id, str):
            raise VisualIdentityError("CURRENT_ASSET_INVALID")
        asset = by_id.get(asset_id)
        if asset is None or asset.scope != scope or asset.state != "CANONICAL":
            raise VisualIdentityError("CURRENT_ASSET_INVALID")

    for scope, asset_id in profile.active_candidate.items():
        if scope not in _ALLOWED_SCOPES or not isinstance(asset_id, str):
            raise VisualIdentityError("ACTIVE_CANDIDATE_INVALID")
        asset = by_id.get(asset_id)
        if asset is None or asset.scope != scope or asset.state != "CANDIDATE":
            raise VisualIdentityError("ACTIVE_CANDIDATE_INVALID")

    return profile


def load_visual_profile(path: str | Path) -> VisualProfile:
    profile_path = Path(path)
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    profile = validate_visual_profile(data)
    if profile_path.name == "profile.json" and profile_path.parent.name != profile.identity_id:
        raise VisualIdentityError("PROFILE_PATH_IDENTITY_MISMATCH")
    return profile


def resolve_bus_avatar(
    profile: VisualProfile | Mapping[str, Any], *, allow_candidate: bool = False
) -> VisualAsset | None:
    validated = validate_visual_profile(profile)
    by_id = {asset.asset_id: asset for asset in validated.assets}

    canonical_id = validated.current.get("bus_avatar")
    if canonical_id:
        return by_id[canonical_id]

    if allow_candidate:
        candidate_id = validated.active_candidate.get("bus_avatar")
        if candidate_id:
            return by_id[candidate_id]

    return None
