"""Digest validation shared by the ledger and tests."""

from __future__ import annotations

import re

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def is_sha256(value: object) -> bool:
    """Return True only for exactly 64 lowercase hexadecimal characters."""

    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def require_sha256(value: object, *, field: str = "sha256") -> str:
    """Validate and return a SHA-256 string, raising ValueError otherwise."""

    if not is_sha256(value):
        raise ValueError(f"{field} must be exactly 64 lowercase hexadecimal characters")
    return value
