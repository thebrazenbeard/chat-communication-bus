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

    authority = qualification["authoritative_qualification"]
    assert qualification["policy"] == "NO_PAID_SERVICES"
    assert authority["mode"] == "LOCAL_NO_PAID_SERVICES"
    assert authority["receipt_required_for_green"] is True
    assert authority["receipt_validator"] == "scripts/radar_validate_qualification_receipt.py"
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
        "scripts/radar_validate_qualification_receipt.py",
        "tests/security/test_no_paid_qualification_consistency.py",
        "tests/security/test_qualification_receipt_admission.py",
    }
    assert required_paths.issubset(set(custody["paths"]))

    validator_command = (
        'py -3.11 scripts/radar_validate_qualification_receipt.py '
        '"$env:TEMP\\radar-local-qualification.json"'
    )
    assert validator_command in operator
    assert "not independent cryptographic attestation" in operator


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


def test_local_runner_preserves_stopped_supabase_database_state() -> None:
    runner = (ROOT / "scripts/radar_local_qualify.ps1").read_text(encoding="utf-8")
    config = tomllib.loads((ROOT / "supabase/config.toml").read_text(encoding="utf-8"))

    assert config["project_id"] == "chat-communication-bus"
    project_id = f'$supabaseProjectId = "{config["project_id"]}"'
    db_resource = '$supabaseDbResource = "supabase_db_$supabaseProjectId"'
    container_probe = 'docker container inspect $supabaseDbResource'
    volume_probe = 'docker volume inspect $supabaseDbResource'
    container_refusal = "Local Supabase database container already exists; refusing destructive qualification"
    volume_refusal = "Local Supabase database volume already exists; refusing destructive qualification"
    cleanup_arm = "$sqlCleanupRequired = $true"
    start = 'Invoke-Checked supabase @("start")'

    for expected in (
        project_id,
        db_resource,
        container_probe,
        volume_probe,
        container_refusal,
        volume_refusal,
    ):
        assert expected in runner

    assert runner.index(container_probe) < runner.index(cleanup_arm)
    assert runner.index(volume_probe) < runner.index(cleanup_arm)
    assert runner.index(container_refusal) < runner.index(start)
    assert runner.index(volume_refusal) < runner.index(start)


def test_local_runner_preserves_all_preexisting_supabase_project_resources() -> None:
    runner = (ROOT / "scripts/radar_local_qualify.ps1").read_text(encoding="utf-8")

    project_label = '$supabaseProjectLabel = "com.supabase.cli.project=$supabaseProjectId"'
    container_list = '@("ps", "-a", "--filter", "label=$supabaseProjectLabel", "--format", "{{.ID}}")'
    volume_list = '@("volume", "ls", "--filter", "label=$supabaseProjectLabel", "--format", "{{.Name}}")'
    network_list = '@("network", "ls", "--filter", "label=$supabaseProjectLabel", "--format", "{{.ID}}")'
    refusal = "Local Supabase project Docker resources already exist; refusing destructive qualification"
    cleanup_arm = "$sqlCleanupRequired = $true"

    for expected in (project_label, container_list, volume_list, network_list, refusal):
        assert expected in runner
        assert runner.index(expected) < runner.index(cleanup_arm)


def test_local_runner_refuses_pass_when_supabase_cleanup_fails() -> None:
    runner = (ROOT / "scripts/radar_local_qualify.ps1").read_text(encoding="utf-8")

    assert "Local Supabase cleanup failed" in runner
    assert 'Write-Warning "Local Supabase stop failed' not in runner


def test_local_runner_preserves_primary_sql_failure_when_cleanup_also_fails() -> None:
    runner = (ROOT / "scripts/radar_local_qualify.ps1").read_text(encoding="utf-8")

    for expected in (
        "$sqlFailure = $null",
        "$cleanupFailure = $null",
        "$sqlFailure = $_",
        "$cleanupFailure = $_",
        "if ($sqlFailure -and $cleanupFailure)",
        "SQL qualification failed:",
        "Local Supabase cleanup failed:",
        "throw $sqlFailure",
    ):
        assert expected in runner
