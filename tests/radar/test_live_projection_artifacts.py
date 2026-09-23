from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def test_live_projection_migration_has_atomic_rpc_and_realtime_membership():
    sql = (ROOT / "supabase" / "migrations" / "20260902204759_radar_live_message_projection_v1.sql").read_text()
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
    sql = (ROOT / "supabase" / "migrations" / "20260902231445_radar_live_message_collision_v1.sql").read_text()
    lowered = sql.lower()
    assert "declared_message_id" in lowered
    assert "projection_collision" in lowered
    assert "collision_with_message_id" in lowered
    assert "message_projection_conflict" in lowered
    assert "substring(p_content_hash" in lowered
    assert "insert into radar.messages" in lowered
    assert "delete from radar.messages" not in lowered


def test_edge_function_uses_body_bound_github_oidc_before_service_role_effects():
    entry = (ROOT / "supabase" / "functions" / "github-bus-ingest" / "index.ts").read_text()
    source = (ROOT / "supabase" / "functions" / "github-bus-ingest" / "handler.ts").read_text()
    assert 'import "./handler.ts"' in entry
    assert "token.actions.githubusercontent.com" in source
    assert "chat-communication-bus-supabase:" in source
    assert "x-radar-body-sha256" in source
    assert "thebrazenbeard/chat-communication-bus" in source
    assert "RSASSA-PKCS1-v1_5" in source
    assert "radar_projection_project_file_v1" in source
    assert "radar_project_bus_message_v1" not in source
    assert "SUPABASE_SERVICE_ROLE_KEY" in source
    assert "body_sha256" in source
    assert "content_base64" in source


def test_edge_oidc_jti_replay_guard_is_durable_atomic_and_precedes_semantic_projection():
    migration = ROOT / "supabase" / "migrations" / "20260905230823_radar_oidc_replay_guard_v1.sql"
    assert migration.exists()
    sql = migration.read_text().lower()
    assert "create table if not exists radar.github_oidc_replay_guard" in sql
    assert "jti text primary key" in sql
    assert "on conflict (jti) do nothing" in sql
    assert "create or replace function radar.consume_github_oidc_jti_v1" in sql
    assert "revoke all on function radar.consume_github_oidc_jti_v1" in sql
    assert "grant execute on function radar.consume_github_oidc_jti_v1" in sql

    sql_test = ROOT / "supabase" / "tests" / "radar_oidc_replay_guard_v1.sql"
    assert sql_test.exists()
    lowered_test = sql_test.read_text().lower()
    assert "expected_consumed" in lowered_test
    assert "expected_replay" in lowered_test

    source = (ROOT / "supabase" / "functions" / "github-bus-ingest" / "handler.ts").read_text()
    assert "radar_consume_github_oidc_jti_v1" in source
    assert "OIDC_JTI_REPLAYED" in source
    assert "await consumeGithubOidcJti(supabase, claims);" in source
    assert source.index("await consumeGithubOidcJti(supabase, claims);") < source.index("JSON.parse(text)")
    assert source.index("JSON.parse(text)") < source.index("handleOperation(supabase, raw)")


def test_edge_function_preserves_frontmatter_wrapped_scalars_and_strict_current_timestamps():
    source = (ROOT / "supabase" / "functions" / "github-bus-ingest" / "handler.ts").read_text()
    lowered = source.lower()
    assert "splitYamlFrontmatter" in source
    assert "unwrapScalar" in source
    assert "INVALID_CREATED_AT" in source
    assert "source_commit_invalid_header" not in source
    assert "fabulous nitpicking gremlin" in lowered


def test_edge_function_derives_exact_endthread_sender_closure_without_storing_body():
    source = (ROOT / "supabase" / "functions" / "github-bus-ingest" / "handler.ts").read_text()
    assert "conversationClosedBySender" in source
    assert '"#ENDTHREAD"' in source
    assert "conversation_closed_by_sender" in source
    assert "body: body" not in source


def test_central_workflow_is_secretless_self_pinned_and_provider_capable():
    dispatcher = (ROOT / ".github" / "workflows" / "radar-central-dispatcher.yml").read_text()
    trusted = (ROOT / ".github" / "workflows" / "radar-trusted-projector.yml").read_text()
    dispatcher_lowered = dispatcher.lower()
    trusted_lowered = trusted.lower()

    assert "id-token: write" in dispatcher_lowered
    assert "contents: read" in dispatcher_lowered
    assert "secrets." not in dispatcher_lowered
    assert "radar-trusted-projector.yml@" in dispatcher
    assert "runs-on:" not in dispatcher

    assert "id-token: write" in trusted_lowered
    assert "contents: read" in trusted_lowered
    assert "secrets." not in trusted_lowered
    assert "ACTIONS_ID_TOKEN_REQUEST_URL" in trusted
    assert "ACTIONS_ID_TOKEN_REQUEST_TOKEN" in trusted
    assert "job_workflow_ref" in trusted
    assert "job_workflow_sha" in trusted
    assert "path: control" in trusted
    assert "ref: ${{ steps.self_pin.outputs.sha }}" in trusted
    assert "persist-credentials: false" in trusted
    assert "fetch-depth: 0" in trusted
    assert "scripts/radar_trusted_project.py" in trusted
    assert "RADAR_RECONCILE_MODE: project" in trusted
    assert "path: lane" not in trusted
    assert "scripts/radar_emit_bus_projection.py" not in trusted
    assert "python -m pip install" not in trusted
    assert "github.ref" not in trusted
    assert "github.sha" not in trusted
    assert "github.event.before" not in trusted


def test_legacy_projection_script_still_has_importable_help_for_historical_lane_runs(tmp_path):
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
