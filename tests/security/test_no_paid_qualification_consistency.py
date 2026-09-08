from __future__ import annotations

import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_no_paid_qualification_contract_is_current_and_source_custodied() -> None:
    qualification = json.loads(
        (ROOT / "architecture/contracts/RADAR_QUALIFICATION_V1.json").read_text(encoding="utf-8")
    )
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))
    custody = json.loads(
        (ROOT / "architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json").read_text(encoding="utf-8")
    )
    operator = (ROOT / "docs/operator/RADAR_NO_PAID_QUALIFICATION.md").read_text(encoding="utf-8")
    validator = (ROOT / "scripts/radar_validate_qualification_receipt.py").read_text(encoding="utf-8")

    authority = qualification["authoritative_qualification"]
    assert qualification["policy"] == "NO_PAID_SERVICES"
    assert authority["mode"] == "LOCAL_NO_PAID_SERVICES"
    assert authority["platform"] == "windows"
    assert authority["launcher_identity_evidentiary"] is False
    assert authority["receipt_required_for_green"] is True
    assert authority["receipt_validator"] == "scripts/radar_validate_qualification_receipt.py"
    assert authority["receipt_location"] == "EXTERNAL_TO_SOURCE_CHECKOUT"
    assert qualification["github_actions"]["private_hosted_actions_authoritative"] is False
    assert qualification["github_actions"]["billing_or_plan_change_allowed_as_recovery"] is False

    assert current["qualification_contract"] == "architecture/contracts/RADAR_QUALIFICATION_V1.json"
    assert current["qualification"]["authoritative_mode"] == "LOCAL_NO_PAID_SERVICES"
    assert current["qualification"]["authorized_platform"] == "windows"
    assert current["qualification"]["launcher_identity_evidentiary"] is False
    assert current["qualification"]["private_hosted_actions_authoritative"] is False
    assert current["qualification"]["billing_or_plan_change_allowed_as_recovery"] is False
    assert current["qualification"]["receipt_validator"] == "scripts/radar_validate_qualification_receipt.py"
    assert current["qualification"]["receipt_location"] == "EXTERNAL_TO_SOURCE_CHECKOUT"

    required_paths = {
        "architecture/contracts/RADAR_QUALIFICATION_V1.json",
        "docs/operator/RADAR_NO_PAID_QUALIFICATION.md",
        "scripts/radar_local_qualify.ps1",
        "scripts/radar_qualify.py",
        "scripts/radar_validate_qualification_receipt.py",
        "tests/security/test_no_paid_qualification_consistency.py",
        "tests/security/test_qualification_receipt_admission.py",
        "tests/security/test_portable_local_qualification.py",
    }
    assert required_paths.issubset(set(custody["paths"]))

    validator_command = (
        'py -3.11 scripts/radar_validate_qualification_receipt.py '
        '"$env:TEMP\\radar-local-qualification.json"'
    )
    assert validator_command in operator
    assert "not independent cryptographic attestation" in operator
    assert "Git cleanliness is necessary but is not a substitute for the external-receipt boundary" in operator
    assert "receipt path must be outside source checkout" in validator
    assert "is_relative_to(repo_root)" in validator


def test_python_qualification_dependency_graph_is_exactly_pinned() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    test_dependencies = set(config["project"]["optional-dependencies"]["test"])
    expected = {
        "pytest==9.1.1",
        'colorama==0.4.6; sys_platform == "win32"',
        "iniconfig==2.3.0",
        "packaging==26.3",
        "pluggy==1.6.0",
        "Pygments==2.21.0",
    }
    assert test_dependencies == expected


def test_python_engine_owns_qualification_semantics_and_windows_launcher_is_thin() -> None:
    qualification = json.loads(
        (ROOT / "architecture/contracts/RADAR_QUALIFICATION_V1.json").read_text(encoding="utf-8")
    )
    current = json.loads((ROOT / "architecture/contracts/RADAR_CURRENT.json").read_text(encoding="utf-8"))
    engine = (ROOT / "scripts/radar_qualify.py").read_text(encoding="utf-8")
    launcher = (ROOT / "scripts/radar_local_qualify.ps1").read_text(encoding="utf-8")

    authority = qualification["authoritative_qualification"]
    assert authority["engine"] == "scripts/radar_qualify.py"
    assert authority["windows_launcher"] == "scripts/radar_local_qualify.ps1"
    assert current["qualification"]["engine"] == "scripts/radar_qualify.py"
    assert current["qualification"]["windows_launcher"] == "scripts/radar_local_qualify.ps1"

    for semantic_token in (
        "read_clean_source_state",
        "required_toolchain",
        "required_stage_instances",
        "supabase_local_start",
        "supabase_db_reset",
        "all_radar_sql_assertions",
        "supabase_local_stop",
        "build_pass_receipt",
    ):
        assert semantic_token in engine

    assert "radar_qualify.py" in launcher
    assert "-3.11" in launcher
    assert "--receipt-path" in launcher
    assert "$LASTEXITCODE" in launcher
    assert "@args" not in launcher
    for forbidden in (
        "supabase db reset",
        "deno check",
        "pytest",
        "radar_source_hashes.py",
        "RADAR_TRUSTED_PROJECTOR_SHA",
        "rev-parse",
        "docker container inspect",
    ):
        assert forbidden.lower() not in launcher.lower()


def test_operator_docs_state_engine_launcher_platform_and_receipt_boundaries() -> None:
    operator = (ROOT / "docs/operator/RADAR_NO_PAID_QUALIFICATION.md").read_text(encoding="utf-8")

    assert "Python engine defines qualification semantics." in operator
    assert "PowerShell is the canonical supported Windows launcher for the currently authorized platform profile." in operator
    assert "Launcher identity is not separately attested by the receipt." in operator
    assert "A runnable engine on another OS is not automatically an authoritative platform profile." in operator
    assert "Receipt V2 stage evidence is required before GREEN." in operator
    assert '$env:TEMP\\radar-local-qualification.json' in operator
    assert "artifacts/radar-local-qualification.json" not in operator
