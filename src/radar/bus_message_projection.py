"""Parse and project bus messages from Git repositories.

Messages are stored as UTF-8 text files with optional YAML frontmatter:

    ---
    message_id: unique-message-id
    writer: sender-name
    created_at: 2026-09-05T10:00:00Z
    intended_recipient: recipient1, recipient2
    requires_ack: yes
    subject: Optional subject
    ---

    Message body here.
    Can contain multiple lines.
    End with #ENDTHREAD to mark conversation as closed.

Or as inline headers (no YAML frontmatter):

    # Title (optional)
    message_id: unique-message-id
    writer: sender-name
    created_at: 2026-09-05T10:00:00Z

    Message body here.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from .supabase_projection import ProjectionCommand

logger = logging.getLogger(__name__)


class BusMessageProjectionError(ValueError):
    """Raised when a bus message document cannot be projected safely."""


# Legacy alias mappings for data consistency across system versions.
# These identities were historically written in different forms and need
# normalization for consistent participant tracking.
_ALIASES = {
    "bridget": "brigit",
    "vera/sol": "vera",
    "vera / sol": "vera",
    "vera-sol": "vera",
}

# Recognized logical identity names. Used to extract the durable identity
# from display-name expansions like "FNG / Fabulous Nitpicking Gremlin".
_RECOGNIZED_IDENTITIES = {
    "fng",
    "radar",
    "brigit",
    "five-five",
    "five",
    "four",
    "six",
    "seven",
    "eight",
    "nine",
    "one",
    "two",
    "three",
    "thirteen",
    "masa",
    "mune",
    "yang",
    "yin",
    "hephaestus",
}

# Matches "key: value" header lines, allowing flexible spacing around the colon
_HEADER_RE = re.compile(r"^(?P<key>[A-Za-z0-9_-]+)\s*:\s*(?P<value>.*)$")

# Boolean values recognized during parsing (case-insensitive)
_TRUE = {"true", "yes", "1"}
_FALSE = {"false", "no", "0"}


@dataclass(frozen=True)
class BusMessageSource:
    """Source metadata for a bus message in a Git repository."""

    repository: str
    ref: str
    branch_head: str
    path: str
    source_commit: str
    blob_sha: str
    source_committed_at: str | None = None


@dataclass(frozen=True)
class ProjectedBusMessage:
    """Normalized representation of a bus message ready for storage."""

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


def _unwrap_scalar(value: str) -> str:
    """Remove surrounding quotes or backticks from a scalar value.

    Args:
        value: The value to unwrap (may be quoted with ', ", or `)

    Returns:
        The unwrapped and stripped value.
    """
    text = value.strip()
    pairs = (("`", "`"), ('"', '"'), ("'", "'"))
    for left, right in pairs:
        if len(text) >= 2 and text.startswith(left) and text.endswith(right):
            return text[1:-1].strip()
    return text


def _normalize_identity(value: str) -> str:
    """Normalize a participant identity to its canonical form.

    Handles:
    - Legacy aliases (e.g., "vera/sol" → "vera")
    - Display-name expansions (e.g., "FNG / Fabulous Nitpicking Gremlin" → "fng")
    - Case normalization (e.g., "Radar" → "radar")

    Args:
        value: The identity string to normalize

    Returns:
        The normalized canonical identity.
    """
    key = _unwrap_scalar(value).strip().casefold()
    if mapped := _ALIASES.get(key):
        return mapped
    # Some early lanes used a display-name expansion after the logical writer,
    # e.g. "FNG / Fabulous Nitpicking Gremlin". Preserve the durable logical
    # identity rather than projecting the prose expansion as a new participant.
    if " / " in key:
        prefix = key.split(" / ", 1)[0].strip()
        if prefix in _RECOGNIZED_IDENTITIES:
            return prefix
    return key


def _parse_bool(value: str | None, *, field: str) -> bool:
    """Parse a boolean value from a message header.

    Args:
        value: The value to parse (None, empty string, or a boolean word)
        field: The field name for error reporting

    Returns:
        True if value matches _TRUE, False if it matches _FALSE or is empty

    Raises:
        BusMessageProjectionError: If value is not a recognized boolean
    """
    if value is None or value.strip() == "":
        return False
    normalized = _unwrap_scalar(value).casefold()
    if normalized in _TRUE:
        return True
    if normalized in _FALSE:
        return False
    raise BusMessageProjectionError(
        f"INVALID_{field.upper()}: expected 'true'/'yes'/'1' or 'false'/'no'/'0', "
        f"got {value!r}"
    )


def _normalize_timestamp(value: str, *, error: str) -> str:
    """Normalize a timestamp to ISO 8601 format with timezone.

    Handles:
    - Date-only input (YYYY-MM-DD) → expanded to full ISO format
    - Various ISO 8601 formats
    - Timezone conversion (Z → +00:00)

    Args:
        value: The timestamp value to normalize
        error: Error message code if normalization fails

    Returns:
        Normalized ISO 8601 timestamp string

    Raises:
        BusMessageProjectionError: If the timestamp cannot be parsed
    """
    text = _unwrap_scalar(value)
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


def _parse_header_line(raw: str, headers: dict[str, str]) -> bool:
    """Parse a single header line and add it to the headers dict.

    Args:
        raw: The raw line to parse
        headers: The headers dict to update (mutated in-place)

    Returns:
        True if the line matched the header format and was added, False otherwise

    Raises:
        BusMessageProjectionError: If a duplicate header key is found
    """
    match = _HEADER_RE.match(raw.rstrip("\r\n"))
    if not match:
        return False
    key = match.group("key").strip().casefold().replace("-", "_")
    if key in headers:
        raise BusMessageProjectionError(f"DUPLICATE_HEADER_{key.upper()}")
    headers[key] = match.group("value").strip()
    return True


def _split_yaml_frontmatter(lines: list[str]) -> tuple[dict[str, str], int] | None:
    """Extract YAML frontmatter from the start of a document.

    YAML frontmatter is delimited by --- on the first non-empty line and
    a closing --- on its own line. Only top-level scalar keys are extracted;
    YAML lists and continuations are ignored to preserve provenance.

    Args:
        lines: The lines of the document (with line endings preserved)

    Returns:
        A tuple of (headers dict, body start index) if frontmatter exists,
        or None if no frontmatter is found

    Raises:
        BusMessageProjectionError: If frontmatter is malformed
    """
    index = 0
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index >= len(lines) or lines[index].strip() != "---":
        return None

    headers: dict[str, str] = {}
    index += 1
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if stripped == "---":
            index += 1
            while index < len(lines) and not lines[index].strip():
                index += 1
            if not headers:
                raise BusMessageProjectionError("HEADER_BLOCK_REQUIRED")
            return headers, index
        # Only top-level scalar keys are needed for projection. YAML list or
        # continuation lines remain provenance in the Git source and are not
        # misclassified as message body.
        if raw[:1].isspace() or stripped.startswith("-"):
            index += 1
            continue
        if stripped and not _parse_header_line(raw, headers):
            raise BusMessageProjectionError("INVALID_FRONTMATTER_HEADER")
        index += 1

    raise BusMessageProjectionError("UNTERMINATED_FRONTMATTER")


def _split_document(text: str) -> tuple[dict[str, str], str]:
    """Split a message document into headers and body.

    Attempts to parse YAML frontmatter first, then falls back to inline headers.
    Inline headers start after an optional single-line title (starting with #)
    and continue until the first blank line.

    Args:
        text: The full message text

    Returns:
        A tuple of (headers dict, body string)

    Raises:
        BusMessageProjectionError: If headers cannot be parsed
    """
    lines = text.splitlines(keepends=True)

    frontmatter = _split_yaml_frontmatter(lines)
    if frontmatter is not None:
        headers, body_index = frontmatter
        return headers, "".join(lines[body_index:])

    index = 0
    while index < len(lines) and not lines[index].strip():
        index += 1
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
        if not _parse_header_line(line, headers):
            if not header_started:
                raise BusMessageProjectionError("HEADER_BLOCK_REQUIRED")
            break
        header_started = True
        index += 1

    if not header_started:
        raise BusMessageProjectionError("HEADER_BLOCK_REQUIRED")

    body = "".join(lines[index:])
    return headers, body


def _conversation_closed_by_sender(body: str) -> bool:
    """Check if the conversation is explicitly closed by the sender.

    A conversation is closed if the last non-whitespace line is "#ENDTHREAD".

    Args:
        body: The message body text

    Returns:
        True if the body ends with #ENDTHREAD, False otherwise
    """
    trimmed = body.rstrip()
    if not trimmed:
        return False
    return trimmed.splitlines()[-1] == "#ENDTHREAD"


def parse_bus_message(content: bytes, source: BusMessageSource) -> ProjectedBusMessage:
    """Parse and normalize a bus message from raw bytes.

    Args:
        content: The raw message content as bytes
        source: Metadata about the message source in Git

    Returns:
        A ProjectedBusMessage with all fields extracted and normalized

    Raises:
        BusMessageProjectionError: If the message format is invalid or required
            fields are missing
    """
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BusMessageProjectionError("MESSAGE_NOT_UTF8") from exc

    headers, body = _split_document(text)

    message_id = _unwrap_scalar(headers.get("message_id", ""))
    if not message_id:
        raise BusMessageProjectionError("MESSAGE_ID_REQUIRED")
    writer = _unwrap_scalar(headers.get("writer", ""))
    if not writer:
        raise BusMessageProjectionError("WRITER_REQUIRED")

    header_created = headers.get("created_at")
    if header_created:
        try:
            created_at = _normalize_timestamp(header_created, error="INVALID_CREATED_AT")
            created_at_basis = "message_header"
        except BusMessageProjectionError:
            if not source.source_committed_at:
                raise
            created_at = _normalize_timestamp(
                source.source_committed_at, error="INVALID_SOURCE_COMMITTED_AT"
            )
            created_at_basis = "source_commit_invalid_header"
    elif source.source_committed_at:
        created_at = _normalize_timestamp(
            source.source_committed_at, error="INVALID_SOURCE_COMMITTED_AT"
        )
        created_at_basis = "source_commit"
    else:
        raise BusMessageProjectionError("CREATED_AT_REQUIRED")

    intended = _unwrap_scalar(headers.get("intended_recipient", ""))
    audience = tuple(
        _normalize_identity(piece) for piece in intended.split(",") if _unwrap_scalar(piece)
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
            "conversation_closed_by_sender": _conversation_closed_by_sender(body),
        }
    )

    subject_raw = headers.get("subject")
    subject = _unwrap_scalar(subject_raw) if subject_raw else None

    logger.debug(
        "Parsed message %s from %s:%s", message_id, source.repository, source.path
    )

    return ProjectedBusMessage(
        message_id=message_id,
        created_at=created_at,
        sender=_normalize_identity(writer),
        audience=audience,
        requires_ack=requires_ack,
        subject=subject,
        full_sha256=full_sha256,
        body_sha256=body_sha256,
        body_length=len(body_bytes),
        source=source,
        metadata=metadata,
    )


def build_bus_projection_command(projected: ProjectedBusMessage) -> ProjectionCommand:
    """Build a SQL projection command for storing the message.

    Args:
        projected: The normalized ProjectedBusMessage

    Returns:
        A ProjectionCommand ready to execute against the database
    """
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
