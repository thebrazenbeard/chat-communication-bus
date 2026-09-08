from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts/radar_validate_qualification_receipt.py"


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


def _init_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "repo"
    contract_dir = repo / "architecture/contracts"
    contract_dir.mkdir(parents=True)
    contract = {
        "policy": "NO_PAID_SERVICES",
        "authoritative_qualification": {
            "mode": "LOCAL_NO_PAID_SERVICES",
            "receipt_required_for_green": True,
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
    (contract_dir / "RADAR_QUALIFICATION_V1.json").write_text(
        json.dumps(contract), encoding="utf-8"
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


def _receipt(commit: str, tree: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "status": "PASS",
        "qualification_mode": "LOCAL_NO_PAID_SERVICES",
        "source_commit": commit,
        "source_tree": tree,
        "working_tree": "CLEAN",
        "python": ["3.11", "3.12"],
        "pip": "26.2.1",
        "deno": "2.9.6",
        "supabase_cli": "2.116.0",
        "completed_at_utc": "2026-09-08T01:00:00+00:00",
    }


def test_accepts_exact_clean_pass_receipt(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(_receipt(commit, tree)), encoding="utf-8")

    result = validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)

    assert result["source_commit"] == commit
    assert result["source_tree"] == tree
    assert result["status"] == "PASS"


def test_rejects_receipt_for_another_commit(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, _commit, tree = _init_repo(tmp_path)
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(_receipt("0" * 40, tree)), encoding="utf-8")

    try:
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)
    except validator.ReceiptValidationError as exc:
        assert "source_commit" in str(exc)
    else:
        raise AssertionError("stale receipt unexpectedly accepted")


def test_rejects_receipt_when_checkout_is_dirty(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(_receipt(commit, tree)), encoding="utf-8")
    (repo / "payload.txt").write_text("mutated\n", encoding="utf-8")

    try:
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)
    except validator.ReceiptValidationError as exc:
        assert "working tree" in str(exc).lower()
    else:
        raise AssertionError("dirty checkout unexpectedly accepted")


def test_rejects_receipt_with_toolchain_drift(tmp_path: Path) -> None:
    validator = _load_validator()
    repo, commit, tree = _init_repo(tmp_path)
    receipt = _receipt(commit, tree)
    receipt["deno"] = "2.9.7"
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    try:
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)
    except validator.ReceiptValidationError as exc:
        assert "deno" in str(exc).lower()
    else:
        raise AssertionError("toolchain drift unexpectedly accepted")
