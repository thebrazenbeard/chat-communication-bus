from types import SimpleNamespace

import pytest

from radar.supabase_provider_reader import (
    ProviderReadbackError,
    SupabaseProviderReader,
)


class FakeQuery:
    def __init__(self, data, calls):
        self.data = data
        self.calls = calls

    def select(self, columns):
        self.calls.append(("select", columns))
        return self

    def eq(self, column, value):
        self.calls.append(("eq", column, value))
        return self

    def limit(self, value):
        self.calls.append(("limit", value))
        return self

    def execute(self):
        self.calls.append(("execute",))
        return SimpleNamespace(data=self.data)


class FakeClient:
    def __init__(self, *, rpc_data=None, table_data=None, fail=None):
        self.rpc_data = rpc_data
        self.table_data = table_data or {}
        self.fail = fail
        self.calls = []

    def rpc(self, name, params):
        self.calls.append(("rpc", name, params))
        if self.fail == "rpc":
            raise RuntimeError("rpc unavailable")
        return FakeQuery(self.rpc_data, self.calls)

    def schema(self, name):
        self.calls.append(("schema", name))
        if self.fail == "schema":
            raise RuntimeError("schema unavailable")
        return self

    def table(self, name):
        self.calls.append(("table", name))
        return FakeQuery(self.table_data.get(name, []), self.calls)


def test_projection_lane_readback_uses_only_read_rpc_and_is_noncanonical():
    client = FakeClient(rpc_data={"projected_head_sha": "abc123"})
    reader = SupabaseProviderReader(client)

    result = reader.read_projection_lane("radar", "bus/radar-v2")

    assert result.surface == "public.radar_projection_get_lane_v1"
    assert result.canonical is False
    assert result.rows == ({"projected_head_sha": "abc123"},)
    assert client.calls == [
        ("rpc", "radar_projection_get_lane_v1", {
            "p_identity_id": "radar",
            "p_branch": "bus/radar-v2",
        }),
        ("execute",),
    ]


def test_missing_projection_lane_is_an_empty_noncanonical_readback():
    result = SupabaseProviderReader(FakeClient(rpc_data=None)).read_projection_lane(
        "radar", "bus/radar-v2"
    )
    assert result.rows == ()
    assert result.canonical is False


def test_operator_view_read_uses_radar_schema_and_bounded_limit():
    client = FakeClient(table_data={
        "identity_message_status_v2": [{"message_id": "m-1"}],
    })
    reader = SupabaseProviderReader(client)

    result = reader.read_identity_message_status("vera", limit=25)

    assert result.surface == "radar.identity_message_status_v2"
    assert result.rows == ({"message_id": "m-1"},)
    assert result.canonical is False
    assert client.calls == [
        ("schema", "radar"),
        ("table", "identity_message_status_v2"),
        ("select", "*"),
        ("eq", "recipient_identity_id", "vera"),
        ("limit", 25),
        ("execute",),
    ]


def test_open_assignments_is_read_only_operator_view():
    client = FakeClient(table_data={"open_assignments_v1": [{"assignment_id": "a-1"}]})
    result = SupabaseProviderReader(client).read_open_assignments(limit=10)
    assert result.rows == ({"assignment_id": "a-1"},)
    assert ("table", "open_assignments_v1") in client.calls


def test_provider_failures_are_bounded_and_do_not_promote_state():
    reader = SupabaseProviderReader(FakeClient(fail="rpc"))
    with pytest.raises(ProviderReadbackError) as exc:
        reader.read_projection_lane("radar", "bus/radar-v2")
    assert exc.value.code == "PROVIDER_READ_FAILED"
    assert "radar_projection_get_lane_v1" in exc.value.detail


def test_invalid_inputs_fail_before_provider_access():
    client = FakeClient()
    reader = SupabaseProviderReader(client)
    with pytest.raises(ProviderReadbackError) as exc:
        reader.read_projection_lane("", "bus/radar-v2")
    assert exc.value.code == "IDENTITY_ID_REQUIRED"
    with pytest.raises(ProviderReadbackError) as exc:
        reader.read_identity_message_status("vera", limit=0)
    assert exc.value.code == "INVALID_LIMIT"
    assert client.calls == []


def test_reader_exposes_no_generic_mutation_or_rpc_escape_hatch():
    reader = SupabaseProviderReader(FakeClient())
    for name in ("insert", "update", "delete", "upsert", "rpc", "table"):
        assert not hasattr(reader, name)


def test_from_credentials_uses_injected_factory_without_exposing_secret():
    calls = []
    client = FakeClient()

    def factory(url, key):
        calls.append((url, key))
        return client

    reader = SupabaseProviderReader.from_credentials(
        "https://example.supabase.co", "secret", client_factory=factory
    )
    assert isinstance(reader, SupabaseProviderReader)
    assert calls == [("https://example.supabase.co", "secret")]
    assert "secret" not in repr(reader)


def test_from_credentials_rejects_blank_url_or_key():
    with pytest.raises(ProviderReadbackError) as exc:
        SupabaseProviderReader.from_credentials("", "key", client_factory=lambda *_: None)
    assert exc.value.code == "PROVIDER_URL_REQUIRED"
    with pytest.raises(ProviderReadbackError) as exc:
        SupabaseProviderReader.from_credentials("https://x", "", client_factory=lambda *_: None)
    assert exc.value.code == "PROVIDER_KEY_REQUIRED"
