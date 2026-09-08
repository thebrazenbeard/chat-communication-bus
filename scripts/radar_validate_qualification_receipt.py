from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def _parse_utc_timestamp(value: Any, *, label: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ReceiptValidationError(f"{label} must be a non-empty timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReceiptValidationError(f"{label} is not ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ReceiptValidationError(f"{label} must be UTC")
    return parsed


def _validate_completed_at(value: Any) -> datetime:
    return _parse_utc_timestamp(value, label="receipt completed_at_utc")


def _canonical_stage_evidence_bytes(stages: list[dict[str, Any]]) -> bytes:
    return json.dumps(
        stages,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _validate_toolchain(receipt: dict[str, Any], required: dict[str, Any]) -> None:
    observed = receipt.get("toolchain")
    if not isinstance(observed, dict):
        raise ReceiptValidationError("receipt toolchain must be a JSON object")

    for key in ("python", "pip", "deno", "supabase_cli"):
        expected = required.get(key)
        value = observed.get(key)
        if value != expected:
            raise ReceiptValidationError(
                f"receipt toolchain {key} mismatch: expected {expected!r}, observed {value!r}"
            )

    for key in ("docker", "psql"):
        expected = required.get(key)
        value = observed.get(key)
        if expected == "required":
            if not isinstance(value, str) or not value.strip():
                raise ReceiptValidationError(
                    f"receipt toolchain {key} must record a non-empty observed identity"
                )
        elif value != expected:
            raise ReceiptValidationError(
                f"receipt toolchain {key} mismatch: expected {expected!r}, observed {value!r}"
            )


def _validate_stage_evidence(receipt: dict[str, Any], authority: dict[str, Any]) -> datetime:
    required = authority.get("required_stage_instances")
    if not isinstance(required, list) or not required or not all(
        isinstance(stage_id, str) and stage_id for stage_id in required
    ):
        raise ReceiptValidationError("qualification contract required_stage_instances is invalid")
    if len(set(required)) != len(required):
        raise ReceiptValidationError("qualification contract required_stage_instances contains duplicates")

    evidence_contract = authority.get("stage_evidence")
    if not isinstance(evidence_contract, dict) or evidence_contract.get("required") is not True:
        raise ReceiptValidationError("qualification contract stage_evidence is invalid")
    if evidence_contract.get("ordinal_base") != 1:
        raise ReceiptValidationError("qualification contract stage_evidence ordinal_base is invalid")
    if evidence_contract.get("digest") != "SHA-256_CANONICAL_JSON":
        raise ReceiptValidationError("qualification contract stage_evidence digest is invalid")

    stages = receipt.get("stages")
    if not isinstance(stages, list):
        raise ReceiptValidationError("receipt stages must be a JSON array")
    if len(stages) != len(required):
        raise ReceiptValidationError(
            f"receipt stage count mismatch: expected {len(required)}, observed {len(stages)}"
        )

    required_fields = evidence_contract.get("required_fields")
    if not isinstance(required_fields, list) or not all(isinstance(field, str) for field in required_fields):
        raise ReceiptValidationError("qualification contract stage_evidence required_fields is invalid")

    previous_completed: datetime | None = None
    for index, (stage, expected_stage_id) in enumerate(zip(stages, required, strict=True), 1):
        if not isinstance(stage, dict):
            raise ReceiptValidationError(f"receipt stage {index} must be a JSON object")
        missing_fields = [field for field in required_fields if field not in stage]
        if missing_fields:
            raise ReceiptValidationError(
                f"receipt stage {index} missing required fields: {', '.join(missing_fields)}"
            )

        ordinal = stage.get("ordinal")
        if isinstance(ordinal, bool) or ordinal != index:
            raise ReceiptValidationError(
                f"receipt stage ordinal mismatch at position {index}: observed {ordinal!r}"
            )
        stage_id = stage.get("stage_id")
        if stage_id != expected_stage_id:
            raise ReceiptValidationError(
                f"receipt stage mismatch at ordinal {index}: expected {expected_stage_id!r}, observed {stage_id!r}"
            )

        exit_code = stage.get("exit_code")
        if isinstance(exit_code, bool) or not isinstance(exit_code, int):
            raise ReceiptValidationError(f"receipt stage {index} exit_code must be an integer")
        if exit_code != 0:
            raise ReceiptValidationError(
                f"receipt stage {index} exit_code must be 0; observed {exit_code}"
            )

        executable = stage.get("executable")
        if not isinstance(executable, str) or not executable.strip():
            raise ReceiptValidationError(f"receipt stage {index} executable must be non-empty")

        for hash_field in ("stdout_sha256", "stderr_sha256"):
            value = stage.get(hash_field)
            if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
                raise ReceiptValidationError(
                    f"receipt stage {index} {hash_field} must be lowercase SHA-256 hex"
                )

        started = _parse_utc_timestamp(
            stage.get("started_at_utc"),
            label=f"receipt stage {index} started_at_utc timestamp",
        )
        completed = _parse_utc_timestamp(
            stage.get("completed_at_utc"),
            label=f"receipt stage {index} completed_at_utc timestamp",
        )
        if completed < started:
            raise ReceiptValidationError(
                f"receipt stage {index} completion time precedes start time"
            )
        if previous_completed is not None and started < previous_completed:
            raise ReceiptValidationError(
                f"receipt stage {index} start time precedes prior stage completion time"
            )
        previous_completed = completed

    declared_digest = receipt.get("stage_evidence_sha256")
    if not isinstance(declared_digest, str) or not _SHA256_RE.fullmatch(declared_digest):
        raise ReceiptValidationError("receipt stage_evidence_sha256 must be lowercase SHA-256 hex")
    actual_digest = hashlib.sha256(_canonical_stage_evidence_bytes(stages)).hexdigest()
    if declared_digest != actual_digest:
        raise ReceiptValidationError(
            f"receipt stage_evidence_sha256 mismatch: expected {actual_digest}, observed {declared_digest}"
        )

    if previous_completed is None:
        raise ReceiptValidationError("receipt stage evidence has no terminal completion timestamp")
    return previous_completed


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
    receipt_schema_version = authority.get("receipt_schema_version")
    if not isinstance(mode, str) or not mode:
        raise ReceiptValidationError("qualification contract mode is invalid")
    if not isinstance(toolchain, dict):
        raise ReceiptValidationError("qualification contract required_toolchain is invalid")
    if isinstance(receipt_schema_version, bool) or not isinstance(receipt_schema_version, int):
        raise ReceiptValidationError("qualification contract receipt_schema_version is invalid")

    _expect(receipt, "schema_version", receipt_schema_version)
    _expect(receipt, "status", "PASS")
    _expect(receipt, "qualification_mode", mode)
    _expect(receipt, "working_tree", "CLEAN")
    _validate_toolchain(receipt, toolchain)
    final_stage_completed = _validate_stage_evidence(receipt, authority)
    receipt_completed = _validate_completed_at(receipt.get("completed_at_utc"))
    if receipt_completed < final_stage_completed:
        raise ReceiptValidationError(
            "receipt completion time precedes final stage completion time"
        )

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
