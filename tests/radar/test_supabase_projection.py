import importlib
import pytest


def _module():
    try:
        return importlib.import_module("radar.supabase_projection")
    except Exception as exc:
        pytest.fail(f"Radar Supabase projection implementation missing: {exc}")


def test_projection_commands_are_parameterized_and_schema_scoped():
    m = _module()
    commands = m.build_projection_commands({"identities": [{"identity_id": "radar", "display_name": "Radar"}]})
    assert commands
    command = commands[0]
    assert command.operation == "UPSERT_IDENTITY"
    assert command.schema == "radar"
    assert command.parameters["identity_id"] == "radar"
    assert "Radar" not in command.sql


def test_projection_contains_no_credentials():
    m = _module()
    commands = m.build_projection_commands({"identities": [{"identity_id": "radar", "display_name": "Radar"}]})
    rendered = "\n".join(c.sql for c in commands).lower()
    assert "service_role" not in rendered
    assert "apikey" not in rendered
    assert "secret" not in rendered


def test_provider_snapshot_parser_keeps_provider_state_as_projection():
    m = _module()
    snapshot = m.parse_provider_snapshot({"protocol_head": "abc", "identities": [{"identity_id": "radar"}]})
    assert snapshot.protocol_head == "abc"
    assert snapshot.canonical is False
