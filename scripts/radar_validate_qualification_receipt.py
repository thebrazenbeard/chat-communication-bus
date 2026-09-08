from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class ReceiptValidationError(ValueError):
    """Raised when a qualification receipt cannot be admitted."""


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"{label} not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReceiptValidationError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ReceiptValidationError(f"{label} must be a JSON object")
    return value


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ReceiptValidationError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def _expect(receipt: dict[str, Any], key: str, expected: Any) -> None:
    observed = receipt.get(key)
    if observed != expected:
        raise ReceiptValidationError(
            f"receipt {key} mismatch: expected {expected!r}, observed {observed!r}"
        )


def _validate_completed_at(value: Any) -> None:
    if not isinstance(value, str) or not value:
        raise ReceiptValidationError("receipt completed_at_utc must be a non-empty timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReceiptValidationError("receipt completed_at_utc is not ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ReceiptValidationError("receipt completed_at_utc must be UTC")


def validate_receipt(*, receipt_path: Path, repo_root: Path | None = None) -> dict[str, Any]:
    repo_root = (repo_root or Path(__file__).resolve().parents[1]).resolve()
    receipt_path = receipt_path.resolve()

    if receipt_path == repo_root or receipt_path.is_relative_to(repo_root):
        raise ReceiptValidationError("receipt path must be outside source checkout")

    contract = _load_json_object(
        repo_root / "architecture/contracts/RADAR_QUALIFICATION_V1.json",
        label="qualification contract",
    )
    receipt = _load_json_object(receipt_path, label="qualification receipt")

    if contract.get("policy") != "NO_PAID_SERVICES":
        raise ReceiptValidationError("qualification contract policy is not NO_PAID_SERVICES")

    authority = contract.get("authoritative_qualification")
    if not isinstance(authority, dict):
        raise ReceiptValidationError("qualification contract authoritative_qualification is invalid")
    if authority.get("receipt_required_for_green") is not True:
        raise ReceiptValidationError("qualification contract no longer requires a receipt for GREEN")

    mode = authority.get("mode")
    toolchain = authority.get("required_toolchain")
    if not isinstance(mode, str) or not mode:
        raise ReceiptValidationError("qualification contract mode is invalid")
    if not isinstance(toolchain, dict):
        raise ReceiptValidationError("qualification contract required_toolchain is invalid")

    _expect(receipt, "schema_version", 1)
    _expect(receipt, "status", "PASS")
    _expect(receipt, "qualification_mode", mode)
    _expect(receipt, "working_tree", "CLEAN")
    _expect(receipt, "python", toolchain.get("python"))
    _expect(receipt, "pip", toolchain.get("pip"))
    _expect(receipt, "deno", toolchain.get("deno"))
    _expect(receipt, "supabase_cli", toolchain.get("supabase_cli"))
    _validate_completed_at(receipt.get("completed_at_utc"))

    top_level = Path(_git(repo_root, "rev-parse", "--show-toplevel")).resolve()
    if top_level != repo_root:
        raise ReceiptValidationError(
            f"repo_root is not the Git top-level: expected {top_level}, observed {repo_root}"
        )

    current_commit = _git(repo_root, "rev-parse", "HEAD")
    current_tree = _git(repo_root, "rev-parse", "HEAD^{tree}")
    working_tree = _git(repo_root, "status", "--porcelain", "--untracked-files=all")
    if working_tree:
        raise ReceiptValidationError("current checkout working tree is not clean")

    _expect(receipt, "source_commit", current_commit)
    _expect(receipt, "source_tree", current_tree)

    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a Radar local qualification receipt against the exact current checkout."
    )
    parser.add_argument("receipt", type=Path, help="Path to the external qualification receipt JSON")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root to validate against; defaults to this script's checkout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        receipt = validate_receipt(receipt_path=args.receipt, repo_root=args.repo_root)
    except ReceiptValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "VALID",
                "source_commit": receipt["source_commit"],
                "source_tree": receipt["source_tree"],
                "qualification_mode": receipt["qualification_mode"],
                "completed_at_utc": receipt["completed_at_utc"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
