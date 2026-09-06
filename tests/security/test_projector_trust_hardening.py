from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / ".github" / "workflows" / "radar-central-dispatcher.yml"
LEGACY_CALLER = ROOT / ".github" / "workflows" / "radar-bus-projection.yml"
TRUSTED = ROOT / ".github" / "workflows" / "radar-trusted-projector.yml"
HANDLER = ROOT / "supabase" / "functions" / "github-bus-ingest" / "handler.ts"
TOPOLOGY = ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_central_dispatcher_delegates_to_immutable_reusable_workflow() -> None:
    source = _source(DISPATCHER)
    match = re.search(
        r"uses:\s*thebrazenbeard/chat-communication-bus/\.github/workflows/"
        r"radar-trusted-projector\.yml@([0-9a-f]{40})",
        source,
    )
    assert match
    assert match, "legacy writer-lane caller must remain immutably contained until Task 9"
    assert "runs-on:" not in source
    assert "id-token: write" in source


def test_default_branch_no_longer_contains_legacy_bus_push_projector() -> None:
    assert not LEGACY_CALLER.exists()


def test_trusted_reusable_workflow_is_workflow_call_only_and_pins_external_actions() -> None:
    source = _source(TRUSTED)
    assert re.search(r"(?m)^\s*workflow_call:\s*$", source)
    assert "push:" not in source
    assert "id-token: write" in source

    action_refs = re.findall(r"uses:\s*(actions/(?:checkout|setup-python))@([^\s#]+)", source)
    assert action_refs
    assert {name for name, _ in action_refs} == {"actions/checkout", "actions/setup-python"}
    for _name, ref in action_refs:
        assert FULL_SHA.fullmatch(ref), f"external action is not pinned immutably: {ref}"


def test_trusted_projector_self_pins_and_runs_only_trusted_central_projector() -> None:
def test_trusted_projector_self_pins_called_workflow_and_never_checks_out_writer_lane():
    source = _source(TRUSTED)
    assert "ACTIONS_ID_TOKEN_REQUEST_URL" in source
    assert "ACTIONS_ID_TOKEN_REQUEST_TOKEN" in source
    assert "job_workflow_ref" in source
    assert "job_workflow_sha" in source
    assert "path: control" in source
    assert "ref: ${{ steps.self_pin.outputs.sha }}" in source
    assert "persist-credentials: false" in source
    assert "fetch-depth: 0" in source

    assert "path: lane" not in source
    assert "github.event.before" not in source
    assert "github.sha" not in source
    assert "github.ref" not in source
    assert "scripts/radar_emit_bus_projection.py" not in source
    assert "scripts/radar_trusted_project.py" in source
    assert "RADAR_RECONCILE_MODE: project" in source


def test_edge_binds_oidc_to_deploy_configured_projection_anchor() -> None:
    source = _source(HANDLER)
    assert 'Deno.env.get("RADAR_TRUSTED_PROJECTOR_SHA")' in source
    assert "EXPECTED_JOB_WORKFLOW_PATH" in source
    assert 'stringClaim(claims, "job_workflow_ref")' in source
    assert 'stringClaim(claims, "job_workflow_sha")' in source
    assert "OIDC_JOB_WORKFLOW_INVALID" in source
    assert "OIDC_JOB_WORKFLOW_SHA_INVALID" in source
    assert "EXPECTED_JOB_WORKFLOW_SHA" not in source


def test_edge_sender_is_lane_derived_and_writer_is_only_a_consistency_assertion() -> None:
    source = _source(HANDLER)
    assert "lane_identity" in source
    assert "WRITER_LANE_MISMATCH" in source
    assert "p_sender: writer" not in source
    assert re.search(r"p_sender:\s*batch\.lane_identity", source)


def test_edge_requires_body_lane_identity_to_match_body_ref_shape() -> None:
    source = _source(HANDLER)
    assert "LANE_IDENTITY_REF_MISMATCH" in source
    assert "laneIdentityFromRef" in source

    topology = json.loads(_source(TOPOLOGY))
    for identity, lane in topology["required_writer_lanes"].items():
        branch = lane["branch"]
        assert re.fullmatch(r"bus/[a-z0-9-]+-v\d+", branch)
        if identity == "brigit":
            assert branch.startswith("bus/bridget-")


def test_edge_projection_concurrency_fails_closed_and_is_bounded() -> None:
    source = _source(HANDLER)
    assert "PROJECT_CONCURRENCY_INVALID" in source
    assert "MAX_PROJECT_CONCURRENCY" in source
    assert "parseProjectConcurrency" in source
    assert 'Number(Deno.env.get("PROJECT_CONCURRENCY") ?? "4")' not in source
