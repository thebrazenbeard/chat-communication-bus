"""Versioned, transport-neutral Radar message envelope."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import uuid
from typing import Mapping

from .model import EnvelopeClassification


ALLOWED_DOMAINS = frozenset(
    {
        "system",
        "llm",
        "ui",
        "database",
        "coordination",
        "security",
        "chat_bus",
        "protocol",
        "repository",
    }
)
ALLOWED_INTENTS = frozenset(
    {
        "command",
        "query",
        "event",
        "error",
        "telemetry",
        "verification",
        "bus_message",
    }
)


@dataclass(frozen=True)
class RadarEnvelope:
    schema_version: int
    message_id: str
    created_at: str
    sender: str
    audience: tuple[str, ...]
    domain: str
    intent: str
    priority: int
    payload: object
    content_hash: str
    idempotency_key: str
    correlation_id: str | None = None
    root_task_id: str | None = None
    causal_parent_id: str | None = None
    requires_ack: bool = False
    expires_at: str | None = None
    authority_ref: str | None = None
    source_refs: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, object]) -> "EnvelopeResult":
        errors: list[str] = []
        required = ("schema_version", "sender", "domain", "intent", "payload")
        for field in required:
            if field not in raw:
                errors.append(field)

        if errors:
            return EnvelopeResult(EnvelopeClassification.REJECTED, None, tuple(errors))

        try:
            schema_version = int(raw["schema_version"])
        except (TypeError, ValueError):
            return EnvelopeResult(EnvelopeClassification.REJECTED, None, ("schema_version",))
        if schema_version != 1:
            return EnvelopeResult(EnvelopeClassification.REJECTED, None, ("schema_version",))

        sender = _required_text(raw.get("sender"), "sender", errors)
        domain = _required_text(raw.get("domain"), "domain", errors)
        intent = _required_text(raw.get("intent"), "intent", errors)
        if errors:
            return EnvelopeResult(
                EnvelopeClassification.REJECTED,
                None,
                tuple(dict.fromkeys(errors)),
            )

        taxonomy_errors: list[str] = []
        if domain not in ALLOWED_DOMAINS:
            taxonomy_errors.append("domain")
        if intent not in ALLOWED_INTENTS:
            taxonomy_errors.append("intent")
        if taxonomy_errors:
            return EnvelopeResult(
                EnvelopeClassification.DLQ,
                None,
                tuple(taxonomy_errors),
            )

        normalized = False
        message_id_obj = raw.get("message_id")
        if isinstance(message_id_obj, str) and message_id_obj.strip():
            message_id = message_id_obj.strip()
        else:
            message_id = f"rad_{uuid.uuid4().hex[:16]}"
            normalized = True

        created_at_obj = raw.get("created_at")
        if isinstance(created_at_obj, str) and created_at_obj.strip():
            created_at = created_at_obj.strip()
        else:
            created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            normalized = True

        audience_obj = raw.get("audience")
        if audience_obj is None:
            audience: tuple[str, ...] = ()
            normalized = True
        elif isinstance(audience_obj, (list, tuple)) and all(
            isinstance(v, str) and v.strip() for v in audience_obj
        ):
            audience = tuple(v.strip().casefold() for v in audience_obj)
        else:
            errors.append("audience")
            audience = ()

        priority_obj = raw.get("priority")
        if priority_obj is None:
            priority = 3
            normalized = True
        else:
            try:
                priority = int(priority_obj)
            except (TypeError, ValueError):
                priority = -1
            if not 0 <= priority <= 4:
                errors.append("priority")

        requires_ack_obj = raw.get("requires_ack", False)
        if not isinstance(requires_ack_obj, bool):
            errors.append("requires_ack")
        requires_ack = bool(requires_ack_obj)

        source_refs_obj = raw.get("source_refs", ())
        if isinstance(source_refs_obj, (list, tuple)) and all(
            isinstance(v, str) for v in source_refs_obj
        ):
            source_refs = tuple(source_refs_obj)
        else:
            errors.append("source_refs")
            source_refs = ()

        if errors:
            return EnvelopeResult(
                EnvelopeClassification.REJECTED,
                None,
                tuple(dict.fromkeys(errors)),
            )

        payload = raw["payload"]
        try:
            payload_json = json.dumps(payload, sort_keys=True)
        except (TypeError, ValueError):
            return EnvelopeResult(EnvelopeClassification.REJECTED, None, ("payload",))

        canonical = {
            "schema_version": schema_version,
            "sender": sender,
            "audience": audience,
            "domain": domain,
            "intent": intent,
            "payload": payload,
        }
        canonical_bytes = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        content_hash = hashlib.sha256(canonical_bytes).hexdigest()

        # Keep provenance hashing separate from the middleware's deterministic
        # duplicate hash. The original Radar middleware hashes only the sorted
        # payload JSON, so caller metadata or caller-selected idempotency values
        # cannot manufacture a different dedupe key for the same payload.
        idempotency_key = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

        envelope = cls(
            schema_version=schema_version,
            message_id=message_id,
            created_at=created_at,
            sender=sender,
            audience=audience,
            domain=domain,
            intent=intent,
            priority=priority,
            payload=payload,
            content_hash=content_hash,
            idempotency_key=idempotency_key,
            correlation_id=_optional_text(raw.get("correlation_id")),
            root_task_id=_optional_text(raw.get("root_task_id")),
            causal_parent_id=_optional_text(raw.get("causal_parent_id")),
            requires_ack=requires_ack,
            expires_at=_optional_text(raw.get("expires_at")),
            authority_ref=_optional_text(raw.get("authority_ref")),
            source_refs=source_refs,
        )
        classification = (
            EnvelopeClassification.NORMALIZED if normalized else EnvelopeClassification.VALID
        )
        return EnvelopeResult(classification, envelope, ())


@dataclass(frozen=True)
class EnvelopeResult:
    classification: EnvelopeClassification
    envelope: RadarEnvelope | None
    errors: tuple[str, ...] = ()


def _required_text(value: object, field: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(field)
        return ""
    return value.strip().casefold()


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


__all__ = [
    "ALLOWED_DOMAINS",
    "ALLOWED_INTENTS",
    "EnvelopeClassification",
    "EnvelopeResult",
    "RadarEnvelope",
]
