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
        if not isinstance(raw, Mapping):
            raise ValueError("IDENTITY_PROJECTION_MUST_BE_MAPPING")
        identity_id = raw.get("identity_id")
        display_name = raw.get("display_name")
        if not isinstance(identity_id, str) or not identity_id.strip():
            raise ValueError("IDENTITY_ID_REQUIRED")
        if not isinstance(display_name, str) or not display_name.strip():
            raise ValueError("DISPLAY_NAME_REQUIRED")
        commands.append(
            ProjectionCommand(
                operation="UPSERT_IDENTITY",
                schema="radar",
                sql=(
                    "insert into radar.identities (identity_id, display_name) "
                    "values (%(identity_id)s, %(display_name)s) "
                    "on conflict (identity_id) do update set display_name = excluded.display_name"
                ),
                parameters={"identity_id": identity_id.strip().casefold(), "display_name": display_name.strip()},
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
        if not isinstance(item, Mapping):
            raise ValueError("INVALID_IDENTITY_SNAPSHOT")
        identities.append(dict(item))
    # Provider projection is never promoted to canonical merely by being read.
    return ProviderSnapshot(protocol_head=protocol, identities=tuple(identities), canonical=False)


__all__ = ["ProjectionCommand", "ProviderSnapshot", "build_projection_commands", "parse_provider_snapshot"]
