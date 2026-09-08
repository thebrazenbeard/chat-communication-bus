from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts/radar_validate_qualification_receipt.py"
REQUIRED_STAGE_INSTANCES = [
    "python_compileall:3.11",
    "python_pytest:3.11",
    "radar_source_hashes:3.11",
    "python_compileall:3.12",
    "python_pytest:3.12",
    "radar_source_hashes:3.12",
    "deno_ci",
    "deno_check",
    "supabase_local_start",
    "supabase_db_reset",
    "all_radar_sql_assertions",
    "supabase_local_stop",
]


def _load_validator():
    spec = importlib.util.spec_from_file_location("radar_validate_qualification_receipt", VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _contract() -> dict[str, object]:
    return {
        "policy": "NO_PAID_SERVICES",
        "authoritative_qualification": {
            "mode": "LOCAL_NO_PAID_SERVICES",
            "receipt_required_for_green": True,
            "receipt_schema_version": 2,
            "required_stage_instances": REQUIRED_STAGE_INSTANCES,
            "required_toolchain": {
                "python": ["3.11", "3.12"],
                "pip": "26.2.1",
                "deno": "2.9.6",
                "supabase_cli": "2.116.0",
                "docker": "required",
                "psql": "required",
            },
        },
    }


def _init_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "repo"
    contract_dir = repo / "architecture/contracts"
    contract_dir.mkdir(parents=True)
    (contract_dir / "RADAR_QUALIFICATION_V1.json").write_text(
        json.dumps(_contract()), encoding="utf-8"
    )
    (repo / "payload.txt").write_text("candidate\n", encoding="utf-8")

    _git(repo, "init")
    _git(repo, "config", "user.name", "Radar Test")
    _git(repo, "config", "user.email", "radar-test@example.invalid")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "candidate")
    commit = _git(repo, "rev-parse", "HEAD")
    tree = _git(repo, "rev-parse", "HEAD^{tree}")
    return repo, commit, tree


def _stage(ordinal: int, stage_id: str) -> dict[str, object]:
    return {
        "ordinal": ordinal,
        "stage_id": stage_id,
        "started_at_utc": "2026-09-08T01:00:00+00:00",
        "completed_at_utc": "2026-09-08T01:00:01+00:00",
        "exit_code": 0,
        "executable": "test-fixture",
        "stdout_sha256": hashlib.sha256(b"stdout").hexdigest(),
        "stderr_sha256": hashlib.sha256(b"").hexdigest(),
    }


def _stage_digest(stages: list[dict[str, object]]) -> str:
    canonical = json.dumps(
        stages,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _receipt(commit: str, tree: str) -> dict[str, object]:
    stages = [_stage(index, stage_id) for index, stage_id in enumerate(REQUIRED_STAGE_INSTANCES, 1)]
    return {
        "schema_version": 2,
        "status": "PASS",
        "qualification_mode": "LOCAL_NO_PAID_SERVICES",
        "source_commit": commit,
        "source_tree": tree,
        "working_tree": "CLEAN",
        "toolchain": {
            "python": ["3.11", "3.12"],
            "pip": "26.2.1",
            "deno": "2.9.6",
            "supabase_cli": "2.116.0",
            "docker": "Docker test fixture",
            "psql": "psql test fixture",
        },
        "stages": stages,
        "stage_evidence_sha256": _stage_digest(stages),
        "completed_at_utc": "2026-09-08T01:01:00+00:00",
    }


def _write_receipt(path: Path, receipt: dict[str, object]) -> None:
    path.write_text(json.dumps(receipt), encoding="utf-8")


def _refresh_digest(receipt: dict[str, object]) -> None:
    stages = receipt["stages"]
    assert isinstance(stages, list)
    receipt["stage_evidence_sha256"] = _stage_digest(stages)


def test_accepts_exact_clean_stage_evidentiary_pass_receipt(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, _receipt(commit, tree))

    result = validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)

    assert result["source_commit"] == commit
    assert result["source_tree"] == tree
    assert result["status"] == "PASS"
    assert result["schema_version"] == 2


def test_rejects_receipt_for_another_commit(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, _commit, tree = _init_repo(tmp_path)
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, _receipt("0" * 40, tree))

    with pytest.raises(validator.ReceiptValidationError, match="source_commit"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


def test_rejects_receipt_when_checkout_is_dirty(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, _receipt(commit, tree))
    (repo / "payload.txt").write_text("mutated\n", encoding="utf-8")

    with pytest.raises(validator.ReceiptValidationError, match="working tree"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


def test_rejects_receipt_with_exact_toolchain_drift(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    toolchain = receipt["toolchain"]
    assert isinstance(toolchain, dict)
    toolchain["deno"] = "2.9.7"
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match="deno"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


@pytest.mark.parametrize("key", ["docker", "psql"])
def test_rejects_receipt_without_required_observed_tool_identity(tmp_path: Path, key: str) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    toolchain = receipt["toolchain"]
    assert isinstance(toolchain, dict)
    toolchain[key] = ""
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match=key):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


def test_rejects_receipt_inside_source_checkout_even_when_git_ignored(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, _commit, _tree = _init_repo(tmp_path)
    (repo / ".gitignore").write_text("ignored-receipts/\n", encoding="utf-8")
    _git(repo, "add", ".gitignore")
    _git(repo, "commit", "-m", "ignore receipt directory")
    commit = _git(repo, "rev-parse", "HEAD")
    tree = _git(repo, "rev-parse", "HEAD^{tree}")

    receipt_dir = repo / "ignored-receipts"
    receipt_dir.mkdir()
    receipt_path = receipt_dir / "receipt.json"
    _write_receipt(receipt_path, _receipt(commit, tree))
    assert _git(repo, "status", "--porcelain", "--untracked-files=all") == ""

    with pytest.raises(validator.ReceiptValidationError, match="outside source checkout"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


def test_rejects_schema_v1_receipt(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    receipt["schema_version"] = 1
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match="schema_version"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


def test_rejects_missing_required_stage(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    stages = receipt["stages"]
    assert isinstance(stages, list)
    stages.pop(3)
    for ordinal, stage in enumerate(stages, 1):
        stage["ordinal"] = ordinal
    _refresh_digest(receipt)
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match="stage"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


def test_rejects_duplicate_stage_in_place_of_required_stage(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    stages = receipt["stages"]
    assert isinstance(stages, list)
    stages[4]["stage_id"] = stages[3]["stage_id"]
    _refresh_digest(receipt)
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match="stage"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


def test_rejects_reordered_complete_stage_set(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    stages = receipt["stages"]
    assert isinstance(stages, list)
    stages[0], stages[1] = stages[1], stages[0]
    for ordinal, stage in enumerate(stages, 1):
        stage["ordinal"] = ordinal
    _refresh_digest(receipt)
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match="stage"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


def test_rejects_nonzero_stage_exit(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    stages = receipt["stages"]
    assert isinstance(stages, list)
    stages[2]["exit_code"] = 1
    _refresh_digest(receipt)
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match="exit_code"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


def test_rejects_stage_ordinal_mismatch(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    stages = receipt["stages"]
    assert isinstance(stages, list)
    stages[5]["ordinal"] = 99
    _refresh_digest(receipt)
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match="ordinal"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("started_at_utc", "2026-09-08T01:00:00"),
        ("completed_at_utc", "2026-09-08T00:59:59+00:00"),
    ],
)
def test_rejects_invalid_stage_timing(tmp_path: Path, field: str, value: str) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    stages = receipt["stages"]
    assert isinstance(stages, list)
    stages[0][field] = value
    _refresh_digest(receipt)
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match="timestamp|UTC|time"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)


def test_rejects_stage_evidence_digest_mismatch(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    receipt["stage_evidence_sha256"] = "0" * 64
    receipt_path = tmp_path / "receipt.json"
    _write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match="stage_evidence_sha256"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)
