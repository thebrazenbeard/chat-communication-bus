import importlib.util
import json
from pathlib import Path

from radar.supabase_provider_reader import ProviderReadback


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "radar_supabase_readback.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("radar_supabase_readback", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeReader:
    def __init__(self):
        self.calls = []

    def read_projection_lane(self, identity_id, branch):
        self.calls.append(("lane", identity_id, branch))
        return ProviderReadback("public.radar_projection_get_lane_v1", ({"head": "abc"},))

    def read_identity_message_status(self, recipient_identity_id, *, limit=100):
        self.calls.append(("messages", recipient_identity_id, limit))
        return ProviderReadback("radar.identity_message_status_v2", ({"message_id": "m1"},))

    def read_open_assignments(self, *, limit=100):
        self.calls.append(("assignments", limit))
        return ProviderReadback("radar.open_assignments_v1", ({"assignment_id": "a1"},))


def test_lane_cli_uses_named_envs_and_never_prints_secret(capsys):
    cli = load_cli()
    reader = FakeReader()
    captured = []

    def factory(url, key):
        captured.append((url, key))
        return reader

    code = cli.main(
        ["--url-env", "U", "--key-env", "K", "lane", "--identity-id", "radar", "--branch", "bus/radar-v2"],
        environ={"U": "https://example.supabase.co", "K": "super-secret"},
        reader_factory=factory,
    )
    assert code == 0
    assert captured == [("https://example.supabase.co", "super-secret")]
    assert reader.calls == [("lane", "radar", "bus/radar-v2")]
    out = capsys.readouterr().out
    assert "super-secret" not in out
    payload = json.loads(out)
    assert payload["canonical"] is False
    assert payload["transport"] == "supabase-py"
    assert payload["rows"] == [{"head": "abc"}]


def test_missing_credential_env_fails_closed_without_calling_factory(capsys):
    cli = load_cli()
    called = False

    def factory(*_args):
        nonlocal called
        called = True
        raise AssertionError("must not initialize provider client")

    code = cli.main(
        ["lane", "--identity-id", "radar", "--branch", "bus/radar-v2"],
        environ={},
        reader_factory=factory,
    )
    assert code == 2
    assert called is False
    payload = json.loads(capsys.readouterr().err)
    assert payload["code"] == "PROVIDER_CREDENTIAL_ENV_MISSING"


def test_messages_and_assignments_subcommands_route_to_read_only_methods(capsys):
    cli = load_cli()
    reader = FakeReader()

    def factory(_url, _key):
        return reader

    env = {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_SERVICE_ROLE_KEY": "secret"}
    assert cli.main(
        ["messages", "--recipient-identity-id", "vera", "--limit", "7"],
        environ=env,
        reader_factory=factory,
    ) == 0
    capsys.readouterr()
    assert cli.main(
        ["assignments", "--limit", "3"],
        environ=env,
        reader_factory=factory,
    ) == 0
    capsys.readouterr()
    assert reader.calls == [("messages", "vera", 7), ("assignments", 3)]
