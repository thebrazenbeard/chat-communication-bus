from __future__ import annotations

import json
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

    assert qualification["policy"] == "NO_PAID_SERVICES"
    assert qualification["authoritative_qualification"]["mode"] == "LOCAL_NO_PAID_SERVICES"
    assert qualification["authoritative_qualification"]["receipt_required_for_green"] is True
    assert qualification["github_actions"]["private_hosted_actions_authoritative"] is False
    assert qualification["github_actions"]["billing_or_plan_change_allowed_as_recovery"] is False

    assert current["qualification_contract"] == "architecture/contracts/RADAR_QUALIFICATION_V1.json"
    assert current["qualification"]["authoritative_mode"] == "LOCAL_NO_PAID_SERVICES"
    assert current["qualification"]["private_hosted_actions_authoritative"] is False
    assert current["qualification"]["billing_or_plan_change_allowed_as_recovery"] is False

    required_paths = {
        "architecture/contracts/RADAR_QUALIFICATION_V1.json",
        "docs/operator/RADAR_NO_PAID_QUALIFICATION.md",
        "scripts/radar_local_qualify.ps1",
        "tests/security/test_no_paid_qualification_consistency.py",
    }
    assert required_paths.issubset(set(custody["paths"]))


def test_local_runner_preserves_frozen_ci_toolchain_and_exact_source_binding() -> None:
    qualification = json.loads(
        (ROOT / "architecture/contracts/RADAR_QUALIFICATION_V1.json").read_text(encoding="utf-8")
    )
    runner = (ROOT / "scripts/radar_local_qualify.ps1").read_text(encoding="utf-8")

    toolchain = qualification["authoritative_qualification"]["required_toolchain"]
    assert toolchain["python"] == ["3.11", "3.12"]
    assert toolchain["pip"] == "26.2.1"
    assert toolchain["deno"] == "2.9.6"
    assert toolchain["supabase_cli"] == "2.116.0"

    for expected in (
        '"3.11", "3.12"',
        'pip==26.2.1',
        'deno 2.9.6',
        '2.116.0',
        'rev-parse", "HEAD^{tree}',
        'status", "--porcelain',
        'working_tree = "CLEAN"',
        'qualification_mode = "LOCAL_NO_PAID_SERVICES"',
    ):
        assert expected in runner


def test_local_runner_revalidates_source_binding_after_all_qualification_stages() -> None:
    runner = (ROOT / "scripts/radar_local_qualify.ps1").read_text(encoding="utf-8")

    # The receipt may claim CLEAN/exact-source only if those facts are re-read
    # after every potentially mutating build/test/tool invocation has completed.
    assert runner.count('status", "--porcelain') >= 2
    assert runner.count('rev-parse", "HEAD") >= 2
    assert runner.count('rev-parse", "HEAD^{tree}') >= 2
    assert "Source commit changed during qualification" in runner
    assert "Source tree changed during qualification" in runner
    assert "Working tree changed during qualification" in runner


def test_local_runner_cannot_self_invalidate_receipt_inside_source_checkout() -> None:
    runner = (ROOT / "scripts/radar_local_qualify.ps1").read_text(encoding="utf-8")
    operator = (ROOT / "docs/operator/RADAR_NO_PAID_QUALIFICATION.md").read_text(encoding="utf-8")

    assert "Receipt path must be outside source checkout" in runner
    assert "IsPathRooted" in runner
    assert "OrdinalIgnoreCase" in runner
    assert '$env:TEMP\\radar-local-qualification.json' in operator
    assert "artifacts/radar-local-qualification.json" not in operator


def test_local_runner_preserves_preexisting_supabase_stack_and_cleans_partial_start() -> None:
    runner = (ROOT / "scripts/radar_local_qualify.ps1").read_text(encoding="utf-8")

    preflight = 'throw "Local Supabase stack is already running; refusing destructive qualification"'
    cleanup_arm = "$sqlCleanupRequired = $true"
    start = 'Invoke-Checked supabase @("start")'
    cleanup_guard = "if ($sqlCleanupRequired)"

    assert preflight in runner
    assert cleanup_arm in runner
    assert cleanup_guard in runner
    assert runner.index(preflight) < runner.index(cleanup_arm) < runner.index(start)
    assert runner.index(cleanup_guard) > runner.index(start)
