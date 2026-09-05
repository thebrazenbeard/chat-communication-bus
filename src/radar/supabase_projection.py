"""Pure provider-projection commands for Radar's Supabase adapter.

This module contains no credentials and performs no network I/O. It translates
Radar state into parameterized, schema-scoped commands that an operator/runtime
may execute through an authorized provider client.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


# Schema and priority validation constants
_ALLOWED_SCHEMAS = {"radar"}
_MIN_PRIORITY = 0
_MAX_PRIORITY = 4


class ProjectionError(ValueError):
    """Custom exception for projection validation errors."""

    def __init__(self, code: str, message: str = ""):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class ProjectionCommand:
    operation: str
    schema: str
    sql: str
    parameters: dict[str, object]


@dataclass(frozen=True)
class ProviderSnapshot:
    protocol_head: str | None
    identities: tuple[dict[str, object], ...]
    canonical: bool = False


def build_projection_commands(state: Mapping[str, object]) -> tuple[ProjectionCommand, ...]:
    """Build projection commands from Radar state.

    Args:
        state: A Mapping containing optional 'identities', 'endpoints', and 'subscriptions' keys.

    Returns:
        A tuple of ProjectionCommand objects ready for execution.

    Raises:
        ProjectionError: If state is invalid or contains malformed records.
    """
    commands: list[ProjectionCommand] = []

    identities = state.get("identities", ()) or ()
    for raw in identities:
        record = _mapping(raw, "IDENTITY_PROJECTION_MUST_BE_MAPPING")
        identity_id = _required_text(record, "identity_id", "IDENTITY_ID_REQUIRED")
        display_name = _required_text(record, "display_name", "DISPLAY_NAME_REQUIRED")
        commands.append(
            _build_upsert_command(
                "UPSERT_IDENTITY",
                "radar",
                (
                    "insert into radar.identities (identity_id, display_name) "
                    "values (%(identity_id)s, %(display_name)s) "
                    "on conflict (identity_id) do update set display_name = excluded.display_name, updated_at = now()"
                ),
                {"identity_id": identity_id.casefold(), "display_name": display_name},
            )
        )

    endpoints = state.get("endpoints", ()) or ()
    for raw in endpoints:
        record = _mapping(raw, "ENDPOINT_PROJECTION_MUST_BE_MAPPING")
        endpoint_id = _required_text(record, "endpoint_id", "ENDPOINT_ID_REQUIRED")
        identity_id = _required_text(record, "identity_id", "IDENTITY_ID_REQUIRED")
        transport = _required_text(record, "transport", "TRANSPORT_REQUIRED")
        address = _required_text(record, "address", "ADDRESS_REQUIRED")
        status = str(record.get("status", "ACTIVE")).strip().upper() or "ACTIVE"
        commands.append(
            _build_upsert_command(
                "UPSERT_ENDPOINT",
                "radar",
                (
                    "insert into radar.endpoints (endpoint_id, identity_id, transport, address, status) "
                    "values (%(endpoint_id)s, %(identity_id)s, %(transport)s, %(address)s, %(status)s) "
                    "on conflict (endpoint_id) do update set identity_id = excluded.identity_id, "
                    "transport = excluded.transport, address = excluded.address, status = excluded.status, updated_at = now()"
                ),
                {
                    "endpoint_id": endpoint_id,
                    "identity_id": identity_id.casefold(),
                    "transport": transport.casefold(),
                    "address": address,
                    "status": status,
                },
            )
        )

    subscriptions = state.get("subscriptions", ()) or ()
    for raw in subscriptions:
        record = _mapping(raw, "SUBSCRIPTION_PROJECTION_MUST_BE_MAPPING")
        identity_id = _required_text(record, "identity_id", "IDENTITY_ID_REQUIRED")
        domain = _required_text(record, "domain", "DOMAIN_REQUIRED")
        intent_obj = record.get("intent")
        if intent_obj is not None and not isinstance(intent_obj, str):
            raise ProjectionError("INVALID_INTENT", f"intent must be a string, got {type(intent_obj).__name__}")
        intent = intent_obj.strip().casefold() if isinstance(intent_obj, str) and intent_obj.strip() else None
        min_priority = int(record.get("min_priority", 3))
        if not _MIN_PRIORITY <= min_priority <= _MAX_PRIORITY:
            raise ProjectionError(
                "INVALID_PRIORITY",
                f"min_priority must be between {_MIN_PRIORITY} and {_MAX_PRIORITY}, got {min_priority}",
            )
        active = bool(record.get("active", True))
        commands.append(
            _build_upsert_command(
                "UPSERT_SUBSCRIPTION",
                "radar",
                (
                    "insert into radar.subscriptions (identity_id, domain, intent, min_priority, active) "
                    "values (%(identity_id)s, %(domain)s, %(intent)s, %(min_priority)s, %(active)s) "
                    "on conflict (identity_id, domain, coalesce(intent, ''), min_priority) "
                    "do update set active = excluded.active"
                ),
                {
                    "identity_id": identity_id.casefold(),
                    "domain": domain.casefold(),
                    "intent": intent,
                    "min_priority": min_priority,
                    "active": active,
                },
            )
        )

    return tuple(commands)


def parse_provider_snapshot(raw: Mapping[str, object]) -> ProviderSnapshot:
    """Parse and validate a provider snapshot.

    Args:
        raw: A Mapping containing optional 'protocol_head' and 'identities' keys.

    Returns:
        A validated ProviderSnapshot object.

    Raises:
        ProjectionError: If the snapshot structure is invalid.
    """
    protocol = raw.get("protocol_head")
    if protocol is not None and not isinstance(protocol, str):
        raise ProjectionError("INVALID_PROTOCOL_HEAD", f"protocol_head must be a string, got {type(protocol).__name__}")
    identities_obj = raw.get("identities", ()) or ()
    if not isinstance(identities_obj, (list, tuple)):
        raise ProjectionError(
            "INVALID_IDENTITIES", f"identities must be a list or tuple, got {type(identities_obj).__name__}"
        )
    identities: list[dict[str, object]] = []
    for item in identities_obj:
        identities.append(dict(_mapping(item, "INVALID_IDENTITY_SNAPSHOT")))
    # Provider projection is never promoted to canonical merely by being read.
    return ProviderSnapshot(protocol_head=protocol, identities=tuple(identities), canonical=False)


def _build_upsert_command(
    operation: str,
    schema: str,
    sql: str,
    parameters: dict[str, object],
) -> ProjectionCommand:
    """Build a ProjectionCommand for an UPSERT operation.

    Args:
        operation: The operation name (e.g., "UPSERT_IDENTITY").
        schema: The database schema (must be in _ALLOWED_SCHEMAS).
        sql: The parameterized SQL string.
        parameters: The parameters dict for the SQL query.

    Returns:
        A ProjectionCommand ready for execution.

    Raises:
        ProjectionError: If the schema is not allowed.
    """
    if schema not in _ALLOWED_SCHEMAS:
        raise ProjectionError("INVALID_SCHEMA", f"schema must be one of {_ALLOWED_SCHEMAS}, got {schema}")
    return ProjectionCommand(operation=operation, schema=schema, sql=sql, parameters=parameters)


def _mapping(value: object, error: str) -> Mapping[str, object]:
    """Validate that a value is a Mapping.

    Args:
        value: The value to validate.
        error: The error code to raise if validation fails.

    Returns:
        The value cast as a Mapping.

    Raises:
        ProjectionError: If the value is not a Mapping.
    """
    if not isinstance(value, Mapping):
        raise ProjectionError(error, f"expected Mapping, got {type(value).__name__}")
    return value


def _required_text(record: Mapping[str, object], key: str, error: str) -> str:
    """Extract and validate a required text field from a record.

    Args:
        record: The record Mapping.
        key: The field name to extract.
        error: The error code to raise if validation fails.

    Returns:
        The stripped text value.

    Raises:
        ProjectionError: If the field is missing, not a string, or empty after stripping.
    """
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProjectionError(error, f"field '{key}' must be a non-empty string")
    return value.strip()


__all__ = ["ProjectionCommand", "ProviderSnapshot", "ProjectionError", "build_projection_commands", "parse_provider_snapshot"]
