from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def test_live_projection_migration_has_atomic_rpc_and_realtime_membership():
    sql = (ROOT / "supabase" / "migrations" / "20260902_radar_live_message_projection_v1.sql").read_text()
    lowered = sql.lower()
    assert "create or replace function radar.project_bus_message_v1" in lowered
    assert "message_projection_conflict" in lowered
    assert "insert into radar.reconciliation_events" in lowered
    assert "insert into radar.messages" in lowered
    assert "supabase_realtime" in lowered
    assert "radar.messages" in lowered
    assert "radar.identity_visuals" in lowered
    assert "revoke all on function radar.project_bus_message_v1" in lowered
    assert "grant execute on function radar.project_bus_message_v1" in lowered


def test_collision_followup_preserves_both_messages_without_rewriting_git_history():
    sql = (ROOT / "supabase" / "migrations" / "20260902_radar_live_message_collision_v1.sql").read_text()
    lowered = sql.lower()
    assert "declared_message_id" in lowered
    assert "projection_collision" in lowered
    assert "collision_with_message_id" in lowered
    assert "message_projection_conflict" in lowered
    assert "substring(p_content_hash" in lowered
    assert "insert into radar.messages" in lowered
    assert "delete from radar.messages" not in lowered


def test_edge_function_uses_custom_github_oidc_before_service_role_effects():
    entry = (ROOT / "supabase" / "functions" / "github-bus-ingest" / "index.ts").read_text()
    source = (ROOT / "supabase" / "functions" / "github-bus-ingest" / "handler.ts").read_text()
    assert 'import "./handler.ts"' in entry
    assert "token.actions.githubusercontent.com" in source
    assert "chat-communication-bus-supabase" in source
    assert "thebrazenbeard/chat-communication-bus" in source
    assert "RSASSA-PKCS1-v1_5" in source
    assert "radar_project_bus_message_v1" in source
    assert "SUPABASE_SERVICE_ROLE_KEY" in source
    assert "body_sha256" in source
    assert "content_base64" in source


def test_edge_function_accepts_legacy_frontmatter_and_wrapped_scalars_with_evidence_time_fallback():
    source = (ROOT / "supabase" / "functions" / "github-bus-ingest" / "handler.ts").read_text()
    assert "splitYamlFrontmatter" in source
    assert "unwrapScalar" in source
    assert "source_commit_invalid_header" in source
    assert "Fabulous Nitpicking Gremlin" in source


def test_edge_function_derives_exact_endthread_sender_closure_without_storing_body():
    source = (ROOT / "supabase" / "functions" / "github-bus-ingest" / "handler.ts").read_text()
    assert "conversationClosedBySender" in source
    assert '"#ENDTHREAD"' in source
    assert "conversation_closed_by_sender" in source
    assert "body: body" not in source


def test_writer_lane_workflow_is_secretless_and_oidc_scoped():
    workflow = (ROOT / ".github" / "workflows" / "radar-bus-projection.yml").read_text()
    lowered = workflow.lower()
    assert "id-token: write" in lowered
    assert "contents: read" in lowered
    assert "secrets." not in lowered
    assert "python -m pip install -e control" in workflow
    assert "scripts/radar_emit_bus_projection.py" in workflow
    assert "radar/live-message-projection-v1" not in workflow
    assert "refs/heads/bus/" not in workflow  # runtime ref comes from github.ref
    assert "github.event.before" in workflow
    assert "--base" in workflow
    assert "--cutover" in workflow
    assert "--bootstrap-main" in workflow


def test_projection_script_bootstraps_local_src_for_legacy_lane_workflow(tmp_path):
    script = ROOT / "scripts" / "radar_emit_bus_projection.py"
    result = subprocess.run(
        [sys.executable, "-S", str(script), "--help"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_current_writer_lanes_have_fail_closed_path_guard_from_fresh_main_control():
    workflow = (ROOT / ".github" / "workflows" / "writer-lane-guard.yml").read_text()
    script = (ROOT / "scripts" / "radar_validate_writer_lane.py").read_text()
    assert 'branches:\n      - "bus/**"' in workflow
    assert "path: lane" in workflow
    assert "ref: main" in workflow
    assert "path: control" in workflow
    assert "python -m pip install -e control" in workflow
    assert "python control/scripts/radar_validate_writer_lane.py" in workflow
    assert "github.ref" in workflow
    assert "github.sha" in workflow
    assert "github.event.before" in workflow
    assert "--base" in workflow
    assert "--cutover" in workflow
    assert "--bootstrap-main" in workflow
    assert "git -C control rev-parse HEAD" in workflow
    assert "fetch-depth: 0" in workflow
    assert "validate_writer_lane_commit" in script
    assert "RADAR_TOPOLOGY_V1.json" in script
    assert "RADAR_WRITER_LANE_V2_CUTOVER.json" in script
    assert 'parser.add_argument("--base")' in script
    assert 'parser.add_argument("--bootstrap-main")' in script
    assert "WRITER_LANE_VALID" in script
