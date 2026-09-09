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
    assert 'repository = "thebrazenbeard/chat-communication-bus"' in source
    assert 'workflow_path = ".github/workflows/radar-trusted-projector.yml"' in source
    assert 'expected_ref = f"{repository}/{workflow_path}@{job_workflow_sha}"' in source
    assert "GITHUB_OUTPUT" in source


def test_reusable_projector_separates_immutable_code_from_current_canonical_data() -> None:
    source = TRUSTED.read_text(encoding="utf-8")

    assert "path: control" in source
    assert "ref: ${{ steps.self_pin.outputs.sha }}" in source
    assert "path: canonical" in source
    assert "ref: main" in source
    assert source.count("persist-credentials: false") >= 2
    assert source.count("fetch-depth: 0") >= 2

    assert "radar.trusted_control_snapshot" in source
    assert "--repo-dir canonical" in source
    assert "--topology canonical/architecture/contracts/RADAR_TOPOLOGY_V1.json" in source
    assert "--cutover canonical/architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json" in source
    assert "PYTHONPATH: control/src" in source
    assert "python control/scripts/radar_trusted_project.py" in source

    assert "path: lane" not in source
    assert "PYTHONPATH: canonical" not in source
    assert "python canonical/" not in source
    assert "github.sha" not in source
    assert "github.ref" not in source
    assert "github.event.before" not in source
    assert "scripts/radar_emit_bus_projection.py" not in source
    assert "python -m pip install" not in source


def test_reusable_projector_runs_only_trusted_central_projection_entrypoint() -> None:
    source = TRUSTED.read_text(encoding="utf-8")
    assert "scripts/radar_trusted_project.py" in source
    assert "RADAR_RECONCILE_MODE: project" in source
    assert "scripts/radar_trusted_reconcile.py" not in source
    assert "curl" not in source.lower()


def test_all_external_actions_in_reusable_projector_are_immutable() -> None:
    source = TRUSTED.read_text(encoding="utf-8")
    refs = re.findall(r"uses:\s*(actions/(?:checkout|setup-python))@([^\s#]+)", source)
    assert {name for name, _ in refs} == {"actions/checkout", "actions/setup-python"}
    for _name, ref in refs:
        assert FULL_SHA.fullmatch(ref)
