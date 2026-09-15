"""Read-only Supabase data-plane adapter for Radar provider qualification.

Git remains canonical. Readbacks from this module are evidence about provider
state only and never promote Supabase state to source authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Protocol


class ProviderReadbackError(RuntimeError):
    """Bounded failure at the provider readback boundary."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)


@dataclass(frozen=True)
class ProviderReadback:
    surface: str
    rows: tuple[dict[str, object], ...]
    canonical: bool = False
    transport: str = "supabase-py"


class _Executable(Protocol):
    def execute(self) -> object: ...


ClientFactory = Callable[[str, str], object]


class SupabaseProviderReader:
    """Narrow read-only facade over an injected Supabase client."""

    def __init__(self, client: object) -> None:
        if client is None:
            raise ProviderReadbackError("PROVIDER_CLIENT_REQUIRED")
        self._client = client

    def __repr__(self) -> str:
        return "SupabaseProviderReader(read_only=True)"

    @classmethod
    def from_credentials(
        cls,
        url: str,
        key: str,
        *,
        client_factory: ClientFactory | None = None,
    ) -> "SupabaseProviderReader":
        provider_url = _required_text(url, "PROVIDER_URL_REQUIRED")
        provider_key = _required_text(key, "PROVIDER_KEY_REQUIRED")
        if client_factory is None:
            try:
                from supabase import create_client as client_factory  # type: ignore[assignment]
            except ImportError as exc:
                raise ProviderReadbackError(
                    "SUPABASE_PY_UNAVAILABLE",
                    "install the provider-readback optional dependency",
                ) from exc
        try:
            client = client_factory(provider_url, provider_key)
        except Exception as exc:
            raise ProviderReadbackError(
                "PROVIDER_CLIENT_INIT_FAILED",
                type(exc).__name__,
            ) from exc
        return cls(client)

    def read_projection_lane(self, identity_id: str, branch: str) -> ProviderReadback:
        identity = _required_text(identity_id, "IDENTITY_ID_REQUIRED")
        writer_branch = _required_text(branch, "BRANCH_REQUIRED")
        params = {"p_identity_id": identity, "p_branch": writer_branch}
        response = self._execute_rpc("radar_projection_get_lane_v1", params)
        return ProviderReadback(
            surface="public.radar_projection_get_lane_v1",
            rows=_rows_from_response(response, "public.radar_projection_get_lane_v1"),
        )

    def read_identity_message_status(
        self,
        recipient_identity_id: str,
        *,
        limit: int = 100,
    ) -> ProviderReadback:
        identity = _required_text(recipient_identity_id, "IDENTITY_ID_REQUIRED")
        bounded_limit = _validated_limit(limit)
        response = self._execute_view(
            "identity_message_status_v2",
            filter_pair=("recipient_identity_id", identity),
            limit=bounded_limit,
        )
        return ProviderReadback(
            surface="radar.identity_message_status_v2",
            rows=_rows_from_response(response, "radar.identity_message_status_v2"),
        )

    def read_open_assignments(self, *, limit: int = 100) -> ProviderReadback:
        response = self._execute_view(
            "open_assignments_v1",
            filter_pair=None,
            limit=_validated_limit(limit),
        )
        return ProviderReadback(
            surface="radar.open_assignments_v1",
            rows=_rows_from_response(response, "radar.open_assignments_v1"),
        )

    def _execute_rpc(self, name: str, params: dict[str, object]) -> object:
        try:
            rpc = getattr(self._client, "rpc")
            query = rpc(name, params)
            return query.execute()
        except Exception as exc:
            raise ProviderReadbackError(
                "PROVIDER_READ_FAILED",
                f"{name}:{type(exc).__name__}",
            ) from exc

    def _execute_view(
        self,
        view: str,
        *,
        filter_pair: tuple[str, str] | None,
        limit: int,
    ) -> object:
        try:
            scoped = getattr(self._client, "schema")("radar")
            query = scoped.table(view).select("*")
            if filter_pair is not None:
                query = query.eq(*filter_pair)
            return query.limit(limit).execute()
        except Exception as exc:
            raise ProviderReadbackError(
                "PROVIDER_READ_FAILED",
                f"radar.{view}:{type(exc).__name__}",
            ) from exc


def _required_text(value: str, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProviderReadbackError(code)
    return value.strip()


def _validated_limit(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 1000:
        raise ProviderReadbackError("INVALID_LIMIT")
    return value


def _rows_from_response(response: object, surface: str) -> tuple[dict[str, object], ...]:
    data = getattr(response, "data", None)
    if data is None:
        return ()
    if isinstance(data, Mapping):
        return (dict(data),)
    if isinstance(data, list) and all(isinstance(row, Mapping) for row in data):
        return tuple(dict(row) for row in data)
    raise ProviderReadbackError(
        "INVALID_PROVIDER_RESPONSE",
        f"{surface}:{type(data).__name__}",
    )


__all__ = [
    "ProviderReadback",
    "ProviderReadbackError",
    "SupabaseProviderReader",
]
