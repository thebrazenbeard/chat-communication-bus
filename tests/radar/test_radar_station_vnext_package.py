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
