from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
INSTRUCTIONS = "RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md"
MANIFEST = "RADAR_STATION_INSTALL_MANIFEST.json"
APPROVED_SPEC = "docs/superpowers/specs/2026-09-08-radar-station-vnext-project-design.md"
APPROVED_SPEC_COMMIT = "b61274f604afee5f9a21c67eec307fb5af99ded7"
IMPLEMENTATION_PLAN = "docs/superpowers/plans/2026-09-08-radar-station-vnext-project.md"
PACKAGE_BRANCH = "work/hephaestus-radar-station-vnext-project-20260908"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest() -> dict[str, object]:
    required = (*NATIVE_SOURCES, INSTRUCTIONS)
    missing = [name for name in required if not (PKG / name).is_file()]
    if missing:
        raise SystemExit(f"missing VNext package files: {', '.join(missing)}")

    allowed = set((*required, MANIFEST))
    extras = sorted(p.name for p in PKG.iterdir() if p.is_file() and p.name not in allowed)
    if extras:
        raise SystemExit(f"unexpected VNext package files: {', '.join(extras)}")

    instruction_text = (PKG / INSTRUCTIONS).read_text(encoding="utf-8")
    if len(instruction_text) > 8000:
        raise SystemExit(
            f"native instructions exceed OBSERVED ceiling: {len(instruction_text)} characters"
        )

    hashes = {name: digest(PKG / name) for name in (*NATIVE_SOURCES, INSTRUCTIONS)}
    return {
        "schema_version": 1,
        "package": "RADAR_STATION_VNEXT_V1",
        "package_state": "PACKAGE_CONSTRUCTED / SOURCE_VALIDATION_PENDING / NOT_NATIVE_INSTALLED",
        "package_branch": PACKAGE_BRANCH,
        "approved_spec": {
            "path": APPROVED_SPEC,
            "commit": APPROVED_SPEC_COMMIT,
        },
        "implementation_plan": IMPLEMENTATION_PLAN,
        "native_source_count": len(NATIVE_SOURCES),
        "native_sources": list(NATIVE_SOURCES),
        "repo_install_artifacts": [INSTRUCTIONS, MANIFEST],
        "native_instructions": INSTRUCTIONS,
        "native_instructions_character_count": len(instruction_text),
        "instruction_limit_basis": {
            "evidence_class": "OBSERVED",
            "characters": 8000,
            "universal_or_documented_limit_claimed": False,
        },
        "sha256": hashes,
        "native_install_applied": False,
        "fresh_chat_tested": False,
        "cross_role_tested": False,
        "behaviorally_qualified": False,
        "patrick_accepted": False,
        "active": False,
        "install_order": {
            "project_instructions": INSTRUCTIONS,
            "project_sources": list(NATIVE_SOURCES),
        },
        "qualification_suite": "RADAR_STATION_QUALIFICATION.md",
        "rollback_predecessor": {
            "status": "NOT_YET_CAPTURED",
            "rule": "Capture actual native predecessor/editable state before cutover; do not infer it from GitHub package history.",
        },
        "known_limitations": [
            "GitHub package construction does not prove native Project installation.",
            "Native Project byte identity is unverified until the product surface provides sufficient readback evidence.",
            "Repository source tests do not equal native behavioral qualification.",
            "Mutable pointers in RADAR_STATION_CURRENT_POINTERS.json require fresh owner readback.",
        ],
        "zero_cost_required": True,
    }


def main() -> None:
    manifest = build_manifest()
    output = json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    (PKG / MANIFEST).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
