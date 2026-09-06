from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HANDLER = ROOT / "supabase/functions/github-bus-ingest/handler.ts"


def test_edge_requires_dynamic_body_bound_audience_and_digest_header() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    assert "chat-communication-bus-supabase:${bodySha256}" in source
    assert 'req.headers.get("x-radar-body-sha256")' in source
    assert "BODY_SHA256_HEADER_INVALID" in source
    assert "OIDC_AUDIENCE_INVALID" in source


def test_edge_consumes_jti_after_crypto_binding_but_before_json_semantics() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    raw_pos = source.index("await req.arrayBuffer()")
    digest_pos = source.index("await sha256(rawBodyBytes)")
    verify_pos = source.index("await verifyGithubOidc")
    header_pos = source.index("x-radar-body-sha256")
    consume_pos = source.index("await consumeGithubOidcJti")
    parse_pos = source.index("JSON.parse")

    assert raw_pos < digest_pos < verify_pos
    assert verify_pos < header_pos < consume_pos < parse_pos


def test_edge_trusts_configured_projection_anchor_not_legacy_bus_push_claims() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    assert 'Deno.env.get("RADAR_TRUSTED_PROJECTOR_SHA")' in source
    assert "OIDC_TRUST_ANCHOR_CONFIGURATION_INVALID" in source
    assert 'stringClaim(claims, "event_name")' in source
    assert '"workflow_run"' in source and '"schedule"' in source
    assert "EXPECTED_WORKFLOW_PREFIX" not in source
    assert 'stringClaim(claims, "ref")' not in source
    assert 'stringClaim(claims, "sha")' not in source


def test_semantically_invalid_bound_request_is_parsed_only_after_jti_burn() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    consume_pos = source.index("await consumeGithubOidcJti")
    parse_operation_pos = source.index("parseOperation")
    assert consume_pos < parse_operation_pos
