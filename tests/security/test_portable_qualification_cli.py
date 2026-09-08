from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "scripts/radar_qualify.py"


def test_portable_qualification_script_exposes_receipt_cli() -> None:
    result = subprocess.run(
        [sys.executable, str(ENGINE), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--receipt-path" in result.stdout
    assert "-ReceiptPath" in result.stdout


def test_portable_qualification_script_requires_receipt_path() -> None:
    result = subprocess.run(
        [sys.executable, str(ENGINE)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "receipt" in result.stderr.lower()
