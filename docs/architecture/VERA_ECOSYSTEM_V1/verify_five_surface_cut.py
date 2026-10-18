"""Verify the source-level five-surface architecture cut, not a deployed runtime.

This intentionally cannot approve an architecture, qualify a guest, or authorize
effects. Owner review, independent tests, and target evidence are separate inputs.
Run: python docs/architecture/VERA_ECOSYSTEM_V1/verify_five_surface_cut.py
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_PLACEMENTS = {
    "EXTERNAL_INDEPENDENT": 5, "RESEARCH_ONLY": 36,
    "CLIENT_OPTIONAL": 16, "HOST_SERVICE_OPTIONAL": 14,
    "ARCHIVE_ONLY": 4, "HISTORICAL_PROVENANCE": 7,
    "MONO_EMBEDDED": 7, "PRIVATE_EXCLUDED": 3,
    "VERAOS_STAGED_SOURCE": 3, "VERAOS_BOOT_REQUIRED": 1,
}
CURRENT_STAGE = {"vera-mono": 316, "portal": 89, "pre-active": 18, "volition": 8}
REQUIRED_PER_REPO = (
    "repository", "default_head", "existing_mechanism", "interface_kind",
    "acceptance_gate", "owner", "exclusion", "placement_proposal",
    "promotion_policy", "runtime_admission",
)
UNQUALIFIED_GATES = {"KCONFIG", "IMAGE", "TARGET_IMPORT", "NORMAL_GUI", "COLD_TWO_BOOT", "MODEL"}


def load_artifacts():
    def read(name):
        return json.loads((HERE / name).read_text(encoding="utf-8"))
    return (
        read("VERA_96_PLACEMENT_AND_CONSUMERS_V1.json"),
        read("VERA_96_TYPED_DEPENDENCY_EDGES_V1.json"),
        read("VERAOS_MINIMAL_BOM_V1.json"),
    )


def check_source_cut(portfolio, typed, bom):
    errors = []
    rows = portfolio.get("repositories", [])
    names = [row.get("repository") for row in rows]
    if len(rows) != 96 or len(set(names)) != 96 or set(names) != set(typed.get("repositories", [])):
        errors.append("96-repository name coverage diverges across artifacts")
    if Counter(row.get("placement_proposal") for row in rows) != EXPECTED_PLACEMENTS:
        errors.append("placement distribution differs from frozen 96-repo V1 review")
    for row in rows:
        name = row.get("repository")
        if any(not row.get(field) for field in REQUIRED_PER_REPO):
            errors.append(f"{name}: missing mechanism/interface/owner/admission field")
        if row.get("sibling_repo_import_required") is not False:
            errors.append(f"{name}: proposed sibling consumer became required import")
        admission = row.get("runtime_admission", {})
        if any(admission.get(k) != "UNVERIFIED" for k in ("installed", "selected_route", "live_consumption")):
            errors.append(f"{name}: unproved installation/route/consumption")
        if admission.get("effect_authority") != "NONE_GRANTED":
            errors.append(f"{name}: unapproved effect authority")
        if row.get("in_veraos_minimal_image") is True and row.get("placement_proposal") not in (
                "VERAOS_STAGED_SOURCE", "VERAOS_BOOT_REQUIRED"):
            errors.append(f"{name}: optional repository promoted into mandatory guest")
    edge_rows = typed.get("edges", [])
    proposals = [e for e in edge_rows if e.get("type") == "PROPOSED_CONSUMER"]
    stages = [e for e in edge_rows if e.get("type") == "STAGED_SOURCE_SNAPSHOT"]
    expected = [(r.get("repository"), c) for r in rows for c in r.get("intended_consumers", [])]
    actual = [(e.get("from"), e.get("to")) for e in proposals]
    if len(proposals) != 147 or len(set(actual)) != 147 or set(actual) != set(expected):
        errors.append("147 proposed consumer edges do not match 96-repo consumers")
    if any(a not in set(names) or b not in set(names) for a, b in actual):
        errors.append("proposed consumer endpoint absent from catalog")
    if len(edge_rows) != 151 or any(e.get("type") not in
            {"PROPOSED_CONSUMER", "STAGED_SOURCE_SNAPSHOT"} for e in edge_rows):
        errors.append("unverified edge promoted into a hard runtime import")
    selected = {e.get("to") for e in stages}
    if len(stages) != 4 or selected != set(CURRENT_STAGE) or any(
            e.get("from") != "vera-os" or e.get("not_guest_boot_required") is not True
            for e in stages):
        errors.append("four source-stage links incorrectly typed as guest boot imports")
    if len({e.get("stage_receipt_sha256") for e in stages}) != 1:
        errors.append("four stage links do not share one immutable source receipt")
    bom_stage = {r.get("repo"): r.get("files") for r in bom.get("staged_sources", [])}
    if bom_stage != CURRENT_STAGE or bom.get("staged_total_files") != 431:
        errors.append("current 431-file stage replaced without owner qualification")
    full_portal = next((r for r in rows if r.get("repository") == "portal"), {})
    selected_portal = next((r for r in bom.get("staged_sources", []) if r.get("repo") == "portal"), {})
    if (full_portal.get("placement_proposal") != "HOST_SERVICE_OPTIONAL"
            or full_portal.get("in_veraos_minimal_image") is not False
            or "NOT full host scheduler" not in selected_portal.get("placement", "")):
        errors.append("full PORTAL host conflated with selected 89-file source subset")
    gates = {r.get("gate"): r.get("status") for r in bom.get("acceptance", [])}
    if not UNQUALIFIED_GATES <= set(gates):
        errors.append("VeraOS target/image/guest/model qualification gate absent")
    if any(gates.get(key) in {"PASS", "QUALIFIED", "SOURCE_ONLY_GREEN"}
           for key in UNQUALIFIED_GATES):
        errors.append("unverified target/image/guest/model gate falsely passed")
    if bom.get("image_produces_authority") is not False:
        errors.append("source or image promoted into effect authority")
    return errors


def cut_report(portfolio, typed, bom):
    errors = check_source_cut(portfolio, typed, bom)
    return {
        "schema": "PORTAL_FIVE_SURFACE_SOURCE_CUT_V1",
        "source_baseline_integrity": "PASS" if not errors else "FAIL",
        "repository_dispositions": len(portfolio.get("repositories", [])),
        "proposed_consumer_links": len([
            e for e in typed.get("edges", []) if e.get("type") == "PROPOSED_CONSUMER"]),
        "selected_source_snapshots": len([
            e for e in typed.get("edges", []) if e.get("type") == "STAGED_SOURCE_SNAPSHOT"]),
        "reviewed_five_surface_architecture": "HOLD_PENDING_OWNER_ACCEPTANCE",
        "linux_guest_and_model": "UNQUALIFIED",
        "effect_authority": "NONE_GRANTED",
        "errors": errors,
    }


if __name__ == "__main__":
    report = cut_report(*load_artifacts())
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if not report["errors"] else 1)
