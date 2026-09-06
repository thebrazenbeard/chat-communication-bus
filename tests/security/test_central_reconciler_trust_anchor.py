from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
TRUSTED = ROOT / ".github" / "workflows" / "radar-trusted-projector.yml"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def test_reusable_projector_self_resolves_called_workflow_sha_from_oidc() -> None:
    source = TRUSTED.read_text(encoding="utf-8")
    lowered = source.lower()

    assert "workflow_call:" in source
    assert "id-token: write" in lowered
    assert "ACTIONS_ID_TOKEN_REQUEST_URL" in source
    assert "ACTIONS_ID_TOKEN_REQUEST_TOKEN" in source
    assert "job_workflow_ref" in source
    assert "job_workflow_sha" in source
    assert "thebrazenbeard/chat-communication-bus/.github/workflows/radar-trusted-projector.yml@" in source
    assert "GITHUB_OUTPUT" in source


def test_reusable_projector_checks_out_only_verified_trusted_control_source() -> None:
    source = TRUSTED.read_text(encoding="utf-8")

    assert "path: control" in source
    assert "ref: ${{ steps.self_pin.outputs.sha }}" in source
    assert "persist-credentials: false" in source
    assert "fetch-depth: 0" in source

    assert "path: lane" not in source
    assert "github.sha" not in source
    assert "github.ref" not in source
    assert "github.event.before" not in source
    assert "scripts/radar_emit_bus_projection.py" not in source
    assert "python -m pip install" not in source


def test_reusable_projector_runs_only_trusted_validate_only_reconciler() -> None:
    source = TRUSTED.read_text(encoding="utf-8")
    assert "scripts/radar_trusted_reconcile.py" in source
    assert "RADAR_RECONCILE_MODE: validate-only" in source
    assert "SUPABASE" not in source.upper()
    assert "curl" not in source.lower()


def test_all_external_actions_in_reusable_projector_are_immutable() -> None:
    source = TRUSTED.read_text(encoding="utf-8")
    refs = re.findall(r"uses:\s*(actions/(?:checkout|setup-python))@([^\s#]+)", source)
    assert {name for name, _ in refs} == {"actions/checkout", "actions/setup-python"}
    for _name, ref in refs:
        assert FULL_SHA.fullmatch(ref)
