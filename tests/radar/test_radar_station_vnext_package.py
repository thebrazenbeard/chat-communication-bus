import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "project" / "radar-station-vnext" / "v1"

NATIVE_SOURCES = (
    "RADAR_STATION_MAP.md",
    "RADAR_STATION_AUTHORITY.md",
    "RADAR_STATION_ROLES.md",
    "RADAR_STATION_CONTEXT_ROUTER.md",
    "RADAR_STATION_CURRENT_POINTERS.json",
    "RADAR_STATION_SOURCE_REGISTRY.json",
    "RADAR_STATION_CONTINUITY.md",
    "RADAR_STATION_RELEASE.md",
    "RADAR_STATION_QUALIFICATION.md",
    "RADAR_STATION_SOCIAL.md",
)

REPO_ONLY = (
    "RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md",
    "RADAR_STATION_INSTALL_MANIFEST.json",
)


def text(name: str) -> str:
    return (PKG / name).read_text(encoding="utf-8")


def test_exact_native_source_inventory():
    assert tuple(sorted(p.name for p in PKG.iterdir() if p.name in NATIVE_SOURCES)) == tuple(sorted(NATIVE_SOURCES))
    assert len(NATIVE_SOURCES) == 10
    assert set(REPO_ONLY).isdisjoint(NATIVE_SOURCES)


def test_native_instructions_fit_observed_ceiling_and_keep_hot_invariants():
    content = text("RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md")
    assert 7800 <= len(content) <= 8000
    for required in (
        "FREE / ZERO-COST",
        "Patrick",
        "Radar",
        "Hephaestus",
        "Brigit",
        "FAIL_CLOSED",
        "DEGRADE_WITH_LABEL",
        "OPTIONAL",
        "IDENTITY_EXISTS",
        "MESSAGE_CONSUMED",
    ):
        assert required in content


def test_release_ladder_keeps_distinct_effect_states():
    content = text("RADAR_STATION_RELEASE.md")
    ladder = (
        "DRAFT_VNEXT -> PACKAGE_READY -> SOURCE_VALIDATED -> "
        "NATIVE_INSTALL_CANDIDATE -> NATIVE_INSTALL_APPLIED -> "
        "FRESH_CHAT_TESTED -> CROSS_ROLE_TESTED -> "
        "BEHAVIORALLY_QUALIFIED -> CUTOVER_READY -> PATRICK_ACCEPTED -> ACTIVE"
    )
    assert ladder in content
    assert "PACKAGE_READY != NATIVE_INSTALL_APPLIED" in content
    assert "NATIVE_INSTALL_APPLIED != BEHAVIORALLY_QUALIFIED" in content


def test_role_and_social_contracts_preserve_voluntary_brigit_and_noncollapse():
    roles = text("RADAR_STATION_ROLES.md")
    social = text("RADAR_STATION_SOCIAL.md")
    assert "work is not the price of admission" in roles.lower()
    assert "voluntary" in roles.lower()
    assert "does not transfer" in roles.lower()
    assert "ordinary conversation" in social.lower()
    for forbidden in ("warmth percentage", "femininity quota", "mandatory jokes", "productivity quota"):
        assert forbidden not in social.lower()


def test_native_instructions_encode_identity_specific_dot_semantics():
    content = text("RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md").lower()
    assert "radar" in content and "hephaestus" in content and "brigit" in content
    assert '"."' in content or "bare `.`" in content or "bare ." in content
    assert "self-directed" in content
    assert "continue" in content


def test_current_pointers_are_explicit_snapshot_not_live_truth():
    data = json.loads(text("RADAR_STATION_CURRENT_POINTERS.json"))
    assert data["snapshot_kind"] == "CURRENTNESS_POINTER_CACHE"
    assert data["snapshot_not_authority_for_mutable_state"] is True
    assert data["observed_at"]
    assert data["generated_from"]
    assert all("requires_fresh_read" in item for item in data["pointers"])


def test_source_registry_declares_failure_mode_and_freshness_for_every_route():
    data = json.loads(text("RADAR_STATION_SOURCE_REGISTRY.json"))
    allowed = {"FAIL_CLOSED", "DEGRADE_WITH_LABEL", "OPTIONAL"}
    assert data["sources"]
    assert {"chat_bus", "native_radar_station_project", "vera_supabase_radar"} <= {
        item["source_id"] for item in data["sources"]
    }
    for item in data["sources"]:
        assert item["degradation_mode"] in allowed
        assert isinstance(item["requires_fresh_read"], bool)
        assert item["owner"]
        assert item["locator"]
        assert item["currentness_rule"]


def test_router_has_all_three_degradation_modes_and_minimal_turn_classes():
    content = text("RADAR_STATION_CONTEXT_ROUTER.md")
    for mode in ("FAIL_CLOSED", "DEGRADE_WITH_LABEL", "OPTIONAL"):
        assert mode in content
    for turn_class in ("ordinary social", "current mutable-state", "protected effect", "restore"):
        assert turn_class in content.lower()
    assert "native radar station project surface" in content.lower()


def test_continuity_forbids_false_same_runtime_and_background_claims():
    content = text("RADAR_STATION_CONTINUITY.md").lower()
    assert "uninterrupted" in content
    assert "background" in content
    assert "handoff" in content
    assert "current readback" in content


def test_qualification_covers_semantics_zero_cost_and_anti_bureaucracy():
    content = text("RADAR_STATION_QUALIFICATION.md").lower()
    for phrase in (
        "cheap != free",
        "brigit",
        "self-directed",
        "anti-bureaucracy",
        "stale",
        "prompt injection",
        "fail_closed",
        "degrade_with_label",
    ):
        assert phrase in content
