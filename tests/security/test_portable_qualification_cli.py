from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "scripts/radar_qualify.py"


def _load_engine():
    spec = importlib.util.spec_from_file_location("radar_qualify_cli", ENGINE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_portable_qualification_script_exposes_only_conventional_receipt_cli() -> None:
    result = subprocess.run(
        [sys.executable, str(ENGINE), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--receipt-path" in result.stdout
    assert "-ReceiptPath" not in result.stdout


def test_portable_qualification_script_requires_receipt_path() -> None:
    result = subprocess.run(
        [sys.executable, str(ENGINE)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "receipt" in result.stderr.lower()


def test_portable_qualification_cli_rejects_abbreviated_and_extra_options(tmp_path: Path) -> None:
    receipt = str((tmp_path / "receipt.json").resolve())
    abbreviated = subprocess.run(
        [sys.executable, str(ENGINE), "--rec", receipt],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    extra = subprocess.run(
        [sys.executable, str(ENGINE), "--receipt-path", receipt, "--skip-sql"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert abbreviated.returncode == 2
    assert extra.returncode == 2


def test_portable_qualification_cli_requires_absolute_receipt_path() -> None:
    result = subprocess.run(
        [sys.executable, str(ENGINE), "--receipt-path", "relative-receipt.json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "absolute" in result.stderr.lower()


def test_main_success_writes_exactly_one_json_object_to_stdout(monkeypatch, capsys, tmp_path: Path) -> None:
    engine = _load_engine()
    expected = {"schema_version": 2, "status": "PASS", "source_commit": "a" * 40}
    monkeypatch.setattr(engine, "qualify", lambda **_kwargs: expected)

    result = engine.main(["--receipt-path", str((tmp_path / "receipt.json").resolve())])
    captured = capsys.readouterr()

    assert result == 0
    assert captured.err == ""
    assert json.loads(captured.out) == expected
    assert captured.out.count("\n") == 1


def test_main_qualification_error_is_stderr_only(monkeypatch, capsys, tmp_path: Path) -> None:
    engine = _load_engine()

    def fail(**_kwargs):
        raise engine.QualificationError("fixture failure")

    monkeypatch.setattr(engine, "qualify", fail)
    result = engine.main(["--receipt-path", str((tmp_path / "receipt.json").resolve())])
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert "qualification failed: fixture failure" in captured.err


def test_main_does_not_mask_unexpected_programmer_error(monkeypatch, tmp_path: Path) -> None:
    engine = _load_engine()

    def fail(**_kwargs):
        raise RuntimeError("programmer defect")

    monkeypatch.setattr(engine, "qualify", fail)
    with pytest.raises(RuntimeError, match="programmer defect"):
        engine.main(["--receipt-path", str((tmp_path / "receipt.json").resolve())])
