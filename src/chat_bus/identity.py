"""Logical identity addressing for Chat Bus transports."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

_ADDRESS_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_SLACK_USER_RE = re.compile(r"^[UW][A-Z0-9]+$")


class IdentityError(ValueError):
    """Raised when logical endpoint configuration is ambiguous or invalid."""


def normalize_address(value: str) -> str:
    """Normalize a user-facing logical address to its canonical lookup key."""

    if not isinstance(value, str):
        raise IdentityError("ADDRESS_MUST_BE_TEXT")
    address = value.strip()
    if address.startswith("@"):
        address = address[1:]
    address = address.casefold()
    if not _ADDRESS_RE.fullmatch(address):
        raise IdentityError("INVALID_LOGICAL_ADDRESS")
    return address


@dataclass(frozen=True)
class LogicalEndpoint:
    """A stable Chat Bus endpoint that may be rendered through multiple transports."""

    endpoint_id: str
    display_name: str
    project_scope: str
    aliases: tuple[str, ...] = ()
    slack_user_id: str | None = None
    icon_emoji: str | None = None

    def __post_init__(self) -> None:
        canonical = normalize_address(self.endpoint_id)
        if canonical != self.endpoint_id:
            raise IdentityError("ENDPOINT_ID_MUST_BE_CANONICAL")
        if not self.display_name or not self.display_name.strip():
            raise IdentityError("DISPLAY_NAME_REQUIRED")
        if not self.project_scope or not self.project_scope.strip():
            raise IdentityError("PROJECT_SCOPE_REQUIRED")
        if self.slack_user_id is not None and not _SLACK_USER_RE.fullmatch(self.slack_user_id):
            raise IdentityError("INVALID_SLACK_USER_ID")
        if self.icon_emoji is not None:
            if not (len(self.icon_emoji) >= 3 and self.icon_emoji.startswith(":") and self.icon_emoji.endswith(":")):
                raise IdentityError("INVALID_ICON_EMOJI")

        seen: set[str] = set()
        for alias in self.aliases:
            normalized = normalize_address(alias)
            if normalized == canonical or normalized in seen:
                raise IdentityError("DUPLICATE_ENDPOINT_ALIAS")
            seen.add(normalized)

    @property
    def addresses(self) -> tuple[str, ...]:
        return (self.endpoint_id, *(normalize_address(alias) for alias in self.aliases))


class EndpointRegistry:
    """Immutable alias registry that rejects ambiguous logical addresses."""

    def __init__(self, endpoints: Iterable[LogicalEndpoint]) -> None:
        by_id: dict[str, LogicalEndpoint] = {}
        by_address: dict[str, LogicalEndpoint] = {}
        by_slack_user: dict[str, LogicalEndpoint] = {}

        for endpoint in endpoints:
            if endpoint.endpoint_id in by_id:
                raise IdentityError("DUPLICATE_ENDPOINT_ID")
            by_id[endpoint.endpoint_id] = endpoint

            for address in endpoint.addresses:
                if address in by_address:
                    raise IdentityError("LOGICAL_ADDRESS_COLLISION")
                by_address[address] = endpoint

            if endpoint.slack_user_id is not None:
                if endpoint.slack_user_id in by_slack_user:
                    raise IdentityError("SLACK_USER_ID_COLLISION")
                by_slack_user[endpoint.slack_user_id] = endpoint

        if not by_id:
            raise IdentityError("AT_LEAST_ONE_ENDPOINT_REQUIRED")

        self._by_id = by_id
        self._by_address = by_address
        self._by_slack_user = by_slack_user

    def resolve(self, address: str) -> LogicalEndpoint:
        try:
            key = normalize_address(address)
        except IdentityError as exc:
            raise IdentityError("UNKNOWN_LOGICAL_ENDPOINT") from exc
        endpoint = self._by_address.get(key)
        if endpoint is None:
            raise IdentityError("UNKNOWN_LOGICAL_ENDPOINT")
        return endpoint

    def resolve_slack_user(self, slack_user_id: str) -> LogicalEndpoint:
        endpoint = self._by_slack_user.get(slack_user_id)
        if endpoint is None:
            raise IdentityError("UNKNOWN_SLACK_USER_ENDPOINT")
        return endpoint

    def endpoint_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_id))
