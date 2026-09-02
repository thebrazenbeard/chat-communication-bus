from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import re
from typing import Mapping

from .supabase_projection import ProjectionCommand


class BusMessageProjectionError(ValueError):
    """Raised when a GitHub Bus document cannot be projected safely."""


_ALIASES = {
    "bridget": "brigit",
    "vera/sol": "vera",
    "vera-sol": "vera",
}
_HEADER_RE = re.compile(r"^(?P<key>[A-Za-z0-9_-]+)\s*:\s*(?P<value>.*)$")
_TRUE = {"true", "yes", "1"}
_FALSE = {"false", "no", "0"}


@dataclass(frozen=True)
class BusMessageSource:
    repository: str
    ref: str
    branch_head: str
    path: str
    source_commit: str
    blob_sha: str
    source_committed_at: str | None = None


@dataclass(frozen=True)
class ProjectedBusMessage:
    message_id: str
    created_at: str
    sender: str
    audience: tuple[str, ...]
    requires_ack: bool
    subject: str | None
    full_sha256: str
    body_sha256: str
    body_length: int
    source: BusMessageSource
    metadata: dict[str, object]


def _normalize_identity(value: str) -> str:
    key = value.strip().casefold()
    return _ALIASES.get(key, key)


def _parse_bool(value: str | None, *, field: str) -> bool:
    if value is None or value.strip() == "":
        return False
    normalized = value.strip().casefold()
    if normalized in _TRUE:
        return True
    if normalized in _FALSE:
        return False
    raise BusMessageProjectionError(f"INVALID_{field.upper()}")


def _normalize_timestamp(value: str, *, error: str) -> str:
    text = value.strip()
    if not text:
        raise BusMessageProjectionError(error)
    candidate = text
    if len(candidate) == 10 and re.fullmatch(r"\d{4}-\d{2}-\d{2}", candidate):
        candidate = f"{candidate}T00:00:00Z"
    iso_candidate = candidate[:-1] + "+00:00" if candidate.endswith("Z") else candidate
    try:
        parsed = datetime.fromisoformat(iso_candidate)
    except ValueError as exc:
        raise BusMessageProjectionError(error) from exc
    if parsed.tzinfo is None:
        candidate = f"{candidate}Z"
    return candidate


def _split_document(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines(keepends=True)
    index = 0

    if index < len(lines) and lines[index].lstrip().startswith("#"):
        index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1

    headers: dict[str, str] = {}
    header_started = False
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            if header_started:
                index += 1
                break
            index += 1
            continue
        match = _HEADER_RE.match(line.rstrip("\r\n"))
        if not match:
            if not header_started:
                raise BusMessageProjectionError("HEADER_BLOCK_REQUIRED")
            break
        header_started = True
        key = match.group("key").strip().casefold().replace("-", "_")
        if key in headers:
            raise BusMessageProjectionError(f"DUPLICATE_HEADER_{key.upper()}")
        headers[key] = match.group("value").strip()
        index += 1

    if not header_started:
        raise BusMessageProjectionError("HEADER_BLOCK_REQUIRED")

    body = "".join(lines[index:])
    return headers, body


def parse_bus_message(content: bytes, source: BusMessageSource) -> ProjectedBusMessage:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BusMessageProjectionError("MESSAGE_NOT_UTF8") from exc

    headers, body = _split_document(text)

    message_id = headers.get("message_id", "").strip()
    if not message_id:
        raise BusMessageProjectionError("MESSAGE_ID_REQUIRED")
    writer = headers.get("writer", "").strip()
    if not writer:
        raise BusMessageProjectionError("WRITER_REQUIRED")

    header_created = headers.get("created_at")
    if header_created:
        created_at = _normalize_timestamp(header_created, error="INVALID_CREATED_AT")
        created_at_basis = "message_header"
    elif source.source_committed_at:
        created_at = _normalize_timestamp(source.source_committed_at, error="INVALID_SOURCE_COMMITTED_AT")
        created_at_basis = "source_commit"
    else:
        raise BusMessageProjectionError("CREATED_AT_REQUIRED")

    intended = headers.get("intended_recipient", "")
    audience = tuple(
        _normalize_identity(piece)
        for piece in intended.split(",")
        if piece.strip()
    )

    requires_reply = _parse_bool(headers.get("requires_reply"), field="requires_reply")
    requires_ack_header = _parse_bool(headers.get("requires_ack"), field="requires_ack")
    requires_ack = requires_reply or requires_ack_header

    full_sha256 = hashlib.sha256(content).hexdigest()
    body_bytes = body.encode("utf-8")
    body_sha256 = hashlib.sha256(body_bytes).hexdigest()

    metadata: dict[str, object] = dict(headers)
    # Canonical provider fields are represented separately; retain the raw
    # header map for provenance but never retain the freeform body.
    metadata.update(
        {
            "created_at_basis": created_at_basis,
            "source_repository": source.repository,
            "source_ref": source.ref,
            "source_branch_head": source.branch_head,
            "source_path": source.path,
            "source_commit": source.source_commit,
            "source_blob_sha": source.blob_sha,
            "body_sha256": body_sha256,
            "body_length": len(body_bytes),
        }
    )

    return ProjectedBusMessage(
        message_id=message_id,
        created_at=created_at,
        sender=_normalize_identity(writer),
        audience=audience,
        requires_ack=requires_ack,
        subject=headers.get("subject") or None,
        full_sha256=full_sha256,
        body_sha256=body_sha256,
        body_length=len(body_bytes),
        source=source,
        metadata=metadata,
    )


def build_bus_projection_command(projected: ProjectedBusMessage) -> ProjectionCommand:
    source_refs = (
        f"github://{projected.source.repository}@{projected.source.source_commit}/{projected.source.path}",
        f"github-ref://{projected.source.repository}/{projected.source.ref}@{projected.source.branch_head}",
        f"git-blob:{projected.source.blob_sha}",
    )
    parameters: dict[str, object] = {
        "p_message_id": projected.message_id,
        "p_created_at": projected.created_at,
        "p_sender": projected.sender,
        "p_audience": list(projected.audience),
        "p_requires_ack": projected.requires_ack,
        "p_source_refs": list(source_refs),
        "p_content_hash": projected.full_sha256,
        "p_idempotency_key": f"chat-bus:{projected.message_id}:{projected.full_sha256}",
        "p_payload": dict(projected.metadata),
    }
    return ProjectionCommand(
        operation="PROJECT_BUS_MESSAGE",
        schema="radar",
        sql=(
            "select radar.project_bus_message_v1("
            "%(p_message_id)s, %(p_created_at)s, %(p_sender)s, %(p_audience)s, %(p_requires_ack)s, "
            "%(p_source_refs)s, %(p_content_hash)s, %(p_idempotency_key)s, %(p_payload)s)"
        ),
        parameters=parameters,
    )


__all__ = [
    "BusMessageProjectionError",
    "BusMessageSource",
    "ProjectedBusMessage",
    "parse_bus_message",
    "build_bus_projection_command",
]
