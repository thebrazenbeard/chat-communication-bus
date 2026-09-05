from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
CALLER = ROOT / ".github" / "workflows" / "radar-bus-projection.yml"
TRUSTED = ROOT / ".github" / "workflows" / "radar-trusted-projector.yml"
HANDLER = ROOT / "supabase" / "functions" / "github-bus-ingest" / "handler.ts"
TOPOLOGY = ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_projection_caller_delegates_privileged_work_to_immutable_reusable_workflow():
    source = _source(CALLER)
    match = re.search(
        r"uses:\s*thebrazenbeard/chat-communication-bus/\.github/workflows/"
        r"radar-trusted-projector\.yml@([0-9a-f]{40})",
        source,
    )
    assert match, "writer-lane caller must delegate to an immutable trusted reusable workflow"
    assert "runs-on:" not in source
    assert "id-token: write" in source


def test_trusted_reusable_workflow_is_workflow_call_only_and_pins_external_actions():
    source = _source(TRUSTED)
    assert re.search(r"(?m)^\s*workflow_call:\s*$", source)
    assert "push:" not in source
    assert "id-token: write" in source

    action_refs = re.findall(r"uses:\s*(actions/(?:checkout|setup-python))@([^\s#]+)", source)
    assert action_refs
    assert {name for name, _ in action_refs} == {"actions/checkout", "actions/setup-python"}
    for _name, ref in action_refs:
        assert FULL_SHA.fullmatch(ref), f"external action is not pinned immutably: {ref}"


def test_trusted_projector_uses_caller_event_context_but_trusted_control_source():
    source = _source(TRUSTED)
    assert "github.event.before" in source
    assert "github.sha" in source
    assert "github.ref" in source
    assert "path: lane" in source
    assert "path: control" in source
    control_ref = re.search(r"path:\s*control.*?ref:\s*([0-9a-f]{40})", source, flags=re.S)
    assert control_ref, "trusted control checkout must be pinned to the reusable-workflow source cut"


def test_edge_binds_oidc_to_exact_reusable_workflow_ref_and_sha():
    source = _source(HANDLER)
    assert 'stringClaim(claims, "job_workflow_ref")' in source
    assert 'stringClaim(claims, "job_workflow_sha")' in source
    assert "EXPECTED_JOB_WORKFLOW_REF" in source
    assert "EXPECTED_JOB_WORKFLOW_SHA" in source
    assert "OIDC_JOB_WORKFLOW_INVALID" in source
    assert "OIDC_JOB_WORKFLOW_SHA_INVALID" in source


def test_edge_sender_is_lane_derived_and_writer_is_only_a_consistency_assertion():
    source = _source(HANDLER)
    assert "lane_identity" in source
    assert "WRITER_LANE_MISMATCH" in source
    assert "p_sender: writer" not in source
    assert re.search(r"p_sender:\s*(?:batch\.)?laneIdentity|p_sender:\s*laneIdentity", source)


def test_edge_requires_lane_identity_to_match_authenticated_ref_shape():
    source = _source(HANDLER)
    assert "LANE_IDENTITY_REF_MISMATCH" in source
    assert "laneIdentityFromRef" in source

    topology = json.loads(_source(TOPOLOGY))
    for identity, lane in topology["required_writer_lanes"].items():
        branch = lane["branch"]
        # All currently supported lane refs have a generation suffix; Brigit's
        # historical spelling is normalized by the Edge identity normalizer.
        assert re.fullmatch(r"bus/[a-z0-9-]+-v\d+", branch)
        if identity == "brigit":
            assert branch.startswith("bus/bridget-")


def test_edge_projection_concurrency_fails_closed_and_is_bounded():
    source = _source(HANDLER)
    assert "PROJECT_CONCURRENCY_INVALID" in source
    assert "MAX_PROJECT_CONCURRENCY" in source
    assert "parseProjectConcurrency" in source
    assert 'Number(Deno.env.get("PROJECT_CONCURRENCY") ?? "4")' not in source
