#!/usr/bin/env python3
"""Compare an untrusted Edge readback with an immutable local source checkout.

This is a SOURCE-ONLY diagnostic. A caller-provided JSON payload does not
authenticate the Supabase provider, the deployment actor, the GitHub OIDC
caller, the private mailbox, or a successful projection. Even exact byte
equivalence therefore always yields HOLD, never a release PASS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


SLUG = "github-bus-ingest"
SOURCE_REL = Path("supabase/functions/github-bus-ingest")
REQUIRED_FILES = frozenset(("index.ts", "handler.ts", "provider_503_log.ts", "deno.json"))
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
MAX_SOURCE_FILE_BYTES = 8 * 1024 * 1024
MAX_OBSERVATION_BYTES = 20 * 1024 * 1024


class InvalidObservation(ValueError):
    """Invalid, mutable, unsafe, or incomplete source/provider observation."""


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise InvalidObservation("SOURCE_GIT_CHECK_UNAVAILABLE") from exc


def _committed_bytes(root: Path, filename: str) -> bytes:
    # The index can hide modifications using assume-unchanged/skip-worktree.
    # Read the immutable HEAD tree object rather than trusting git status.
    object_name = f"HEAD:{SOURCE_REL.as_posix()}/{filename}"
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "cat-file", "blob", object_name],
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise InvalidObservation("COMMITTED_SOURCE_BLOB_UNAVAILABLE") from exc


def _require_source_head(root: Path, expected_head: str) -> None:
    if not isinstance(expected_head, str) or HEX40.fullmatch(expected_head) is None:
        raise InvalidObservation("EXPECTED_SOURCE_HEAD_INVALID")
    if Path(_git(root, "rev-parse", "--show-toplevel")).resolve() != root.resolve():
        raise InvalidObservation("SOURCE_ROOT_NOT_GIT_TOPLEVEL")
    if _git(root, "rev-parse", "HEAD") != expected_head:
        raise InvalidObservation("SOURCE_HEAD_MISMATCH")
    if _git(root, "status", "--porcelain", "--untracked-files=all", "--", str(SOURCE_REL)):
        raise InvalidObservation("SOURCE_FILES_DIRTY")


def _validate_snapshot(snapshot: dict[str, object]) -> dict[str, str]:
    if not isinstance(snapshot, dict):
        raise InvalidObservation("PROVIDER_METADATA_NOT_OBJECT")
    if snapshot.get("slug") != SLUG:
        raise InvalidObservation("PROVIDER_SLUG_MISMATCH")
    if not isinstance(snapshot.get("status"), str) or not snapshot["status"]:
        raise InvalidObservation("PROVIDER_STATUS_INVALID")
    if type(snapshot.get("version")) is not int or snapshot["version"] < 1:
        raise InvalidObservation("PROVIDER_VERSION_INVALID")
    if type(snapshot.get("verify_jwt")) is not bool:
        raise InvalidObservation("PROVIDER_VERIFY_JWT_INVALID")
    if not isinstance(snapshot.get("ezbr_sha256"), str) or HEX64.fullmatch(snapshot["ezbr_sha256"]) is None:
        raise InvalidObservation("PROVIDER_BUNDLE_HASH_INVALID")
    entries = snapshot.get("files")
    if not isinstance(entries, list) or len(entries) != len(REQUIRED_FILES):
        raise InvalidObservation("PROVIDER_SOURCE_FILE_SET_INVALID")
    by_name: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise InvalidObservation("PROVIDER_SOURCE_FILE_INVALID")
        name, content = entry.get("name"), entry.get("content")
        if not isinstance(name, str) or name not in REQUIRED_FILES or name in by_name:
            raise InvalidObservation("PROVIDER_SOURCE_NAME_INVALID")
        if not isinstance(content, str):
            raise InvalidObservation("PROVIDER_SOURCE_CONTENT_INVALID")
        if len(content.encode("utf-8")) > MAX_SOURCE_FILE_BYTES:
            raise InvalidObservation("PROVIDER_SOURCE_CONTENT_OVERSIZE")
        by_name[name] = content
    if set(by_name) != REQUIRED_FILES:
        raise InvalidObservation("PROVIDER_SOURCE_FILE_SET_INVALID")
    return by_name


def compare_source_files(
    source_root: Path, expected_head: str, provider_snapshot: dict[str, object]
) -> dict[str, object]:
    """Return only byte-equivalence observations; never deployment authority."""
    root = Path(source_root).resolve(strict=True)
    _require_source_head(root, expected_head)
    observed = _validate_snapshot(provider_snapshot)
    mismatches: list[str] = []
    for filename in sorted(REQUIRED_FILES):
        path = root / SOURCE_REL / filename
        cursor = root
        for part in SOURCE_REL.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise InvalidObservation("SOURCE_PATH_REDIRECTED")
        if path.is_symlink() or not path.is_file():
            raise InvalidObservation("SOURCE_FILE_MISSING_OR_REDIRECTED")
        data = path.read_bytes()
        if len(data) > MAX_SOURCE_FILE_BYTES:
            raise InvalidObservation("SOURCE_FILE_OVERSIZE")
        if data != _committed_bytes(root, filename):
            raise InvalidObservation("SOURCE_BYTES_DIVERGE_FROM_IMMUTABLE_HEAD")
        actual_hash = hashlib.sha256(data).digest()
        observed_hash = hashlib.sha256(observed[filename].encode("utf-8")).digest()
        if actual_hash != observed_hash:
            mismatches.append(filename)
    return {
        "status": "HOLD",
        "evidence_class": "UNTRUSTED_SOURCE_BYTE_COMPARISON",
        "source_head": expected_head,
        "provider_version_claimed": provider_snapshot["version"],
        "provider_bundle_digest_qualified": False,
        "all_files_match": not mismatches,
        "mismatch_files": mismatches,
        "reasons": [
            "DEPLOYMENT_CUSTODY_UNVERIFIED",
            "PROVIDER_BUNDLE_DIGEST_UNBOUND",
            "TRUSTED_CALLER_POLICY_UNQUALIFIED",
            "DELIVERY_UNVERIFIED",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--provider-json", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.provider_json.stat().st_size > MAX_OBSERVATION_BYTES:
            raise InvalidObservation("PROVIDER_OBSERVATION_OVERSIZE")
        snapshot = json.loads(args.provider_json.read_text(encoding="utf-8"))
        result = compare_source_files(args.source_root, args.expected_head, snapshot)
    except (InvalidObservation, ValueError, OSError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["all_files_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
