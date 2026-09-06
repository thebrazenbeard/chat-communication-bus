from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HANDLER = ROOT / "supabase/functions/github-bus-ingest/handler.ts"


def test_edge_requires_dynamic_body_bound_audience_and_digest_header() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    assert 'const AUDIENCE_PREFIX = "chat-communication-bus-supabase:"' in source
    assert 'req.headers.get("x-radar-body-sha256")' in source
    assert "BODY_SHA256_HEADER_INVALID" in source
    assert "BODY_SHA256_MISMATCH" in source
    assert "OIDC_AUDIENCE_INVALID" in source
    assert "`${AUDIENCE_PREFIX}${actualDigest}`" in source


def test_edge_consumes_jti_after_crypto_binding_but_before_json_semantics() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    header_pos = source.index('req.headers.get("x-radar-body-sha256")')
    raw_pos = source.index("await req.arrayBuffer()")
    digest_pos = source.index("await sha256(rawBody)")
    verify_pos = source.index("await verifyGithubOidc")
    consume_pos = source.index("await consumeGithubOidcJti")
    parse_pos = source.index("JSON.parse(text)")

    assert header_pos < raw_pos < digest_pos < verify_pos < consume_pos < parse_pos


def test_edge_trusts_configured_projection_anchor_and_central_caller() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    assert 'Deno.env.get("RADAR_TRUSTED_PROJECTOR_SHA")' in source
    assert "TRUSTED_PROJECTOR_SHA_INVALID" in source
    assert "EXPECTED_CALLER_WORKFLOW_REF" in source
    assert "EXPECTED_JOB_WORKFLOW_PATH" in source
    assert 'stringClaim(claims, "job_workflow_ref")' in source
    assert 'stringClaim(claims, "job_workflow_sha")' in source
    assert '"workflow_run"' in source and '"schedule"' in source
    assert "EXPECTED_WORKFLOW_PREFIX" not in source
    assert 'stringClaim(claims, "sha")' not in source


def test_semantically_invalid_bound_request_is_parsed_only_after_jti_burn() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    consume_pos = source.index("await consumeGithubOidcJti")
    parse_pos = source.index("JSON.parse(text)")
    operation_pos = source.index("handleOperation(supabase, raw)")
    assert consume_pos < parse_pos < operation_pos


def test_edge_exposes_only_fenced_projection_operations() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    for operation in (
        '"cursor"',
        '"set_control_cut"',
        '"claim_batch"',
        '"project_batch"',
        '"finalize_batch"',
    ):
        assert operation in source
    assert "radar_projection_seed_lane_v1" not in source
    assert "radar_projection_record_file_result_v1" in source
