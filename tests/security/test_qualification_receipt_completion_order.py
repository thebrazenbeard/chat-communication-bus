from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts/radar_validate_qualification_receipt.py"
FIXTURE_PATH = ROOT / "tests/security/test_qualification_receipt_admission.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_receipt_completion_cannot_precede_final_stage_completion(tmp_path: Path) -> None:
    validator = _load(VALIDATOR_PATH, "radar_validate_qualification_receipt_completion_test")
    fixtures = _load(FIXTURE_PATH, "radar_qualification_receipt_fixtures")
    repo, commit, tree = fixtures._init_repo(tmp_path)
    receipt = fixtures._receipt(commit, tree)

    final_stage = receipt["stages"][-1]
    assert final_stage["completed_at_utc"] == "2026-09-08T01:00:23+00:00"
    receipt["completed_at_utc"] = "2026-09-08T01:00:22+00:00"
    receipt_path = tmp_path / "receipt.json"
    fixtures._write_receipt(receipt_path, receipt)

    with pytest.raises(validator.ReceiptValidationError, match="completion"):
        validator.validate_receipt(receipt_path=receipt_path, repo_root=repo)
