"""Pure provider-projection commands for Radar's Supabase adapter.

This module contains no credentials and performs no network I/O. It translates
Radar state into parameterized, schema-scoped commands that an operator/runtime
may execute through an authorized provider client.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


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
    commands: list[ProjectionCommand] = []

    identities = state.get("identities", ()) or ()
    for raw in identities:
        record = _mapping(raw, "IDENTITY_PROJECTION_MUST_BE_MAPPING")
        identity_id = _required_text(record, "identity_id", "IDENTITY_ID_REQUIRED")
        display_name = _required_text(record, "display_name", "DISPLAY_NAME_REQUIRED")
        commands.append(
            ProjectionCommand(
                operation="UPSERT_IDENTITY",
                schema="radar",
                sql=(
                    "insert into radar.identities (identity_id, display_name) "
                    "values (%(identity_id)s, %(display_name)s) "
                    "on conflict (identity_id) do update set display_name = excluded.display_name, updated_at = now()"
                ),
                parameters={"identity_id": identity_id.casefold(), "display_name": display_name},
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
            ProjectionCommand(
                operation="UPSERT_ENDPOINT",
                schema="radar",
                sql=(
                    "insert into radar.endpoints (endpoint_id, identity_id, transport, address, status) "
                    "values (%(endpoint_id)s, %(identity_id)s, %(transport)s, %(address)s, %(status)s) "
                    "on conflict (endpoint_id) do update set identity_id = excluded.identity_id, "
                    "transport = excluded.transport, address = excluded.address, status = excluded.status, updated_at = now()"
                ),
                parameters={
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
            raise ValueError("INVALID_INTENT")
        intent = intent_obj.strip().casefold() if isinstance(intent_obj, str) and intent_obj.strip() else None
        min_priority = int(record.get("min_priority", 3))
        if not 0 <= min_priority <= 4:
            raise ValueError("INVALID_PRIORITY")
        active = bool(record.get("active", True))
        commands.append(
            ProjectionCommand(
                operation="UPSERT_SUBSCRIPTION",
                schema="radar",
                sql=(
                    "insert into radar.subscriptions (identity_id, domain, intent, min_priority, active) "
                    "values (%(identity_id)s, %(domain)s, %(intent)s, %(min_priority)s, %(active)s) "
                    "on conflict (identity_id, domain, coalesce(intent, ''), min_priority) "
                    "do update set active = excluded.active"
                ),
                parameters={
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
    protocol = raw.get("protocol_head")
    if protocol is not None and not isinstance(protocol, str):
        raise ValueError("INVALID_PROTOCOL_HEAD")
    identities_obj = raw.get("identities", ()) or ()
    if not isinstance(identities_obj, (list, tuple)):
        raise ValueError("INVALID_IDENTITIES")
    identities: list[dict[str, object]] = []
    for item in identities_obj:
        identities.append(dict(_mapping(item, "INVALID_IDENTITY_SNAPSHOT")))
    # Provider projection is never promoted to canonical merely by being read.
    return ProviderSnapshot(protocol_head=protocol, identities=tuple(identities), canonical=False)


def _mapping(value: object, error: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(error)
    return value


def _required_text(record: Mapping[str, object], key: str, error: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(error)
    return value.strip()


__all__ = ["ProjectionCommand", "ProviderSnapshot", "build_projection_commands", "parse_provider_snapshot"]
