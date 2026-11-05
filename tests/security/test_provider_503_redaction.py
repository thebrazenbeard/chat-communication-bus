from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
EDGE = ROOT / "supabase/functions/github-bus-ingest"
HANDLER = EDGE / "handler.ts"
HELPER = EDGE / "provider_503_log.ts"
CUSTODY = ROOT / "architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json"


def test_handler_redacts_uncaught_errors_and_logs_only_allowlisted_503s() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    assert 'import { provider503LogEvent } from "./provider_503_log.ts";' in source
    assert 'const diagnostic = provider503LogEvent(error.status, error.code);' in source
    assert 'if (diagnostic !== null) console.warn(diagnostic);' in source
    assert 'console.error("RADAR_PROVIDER_INTERNAL_ERROR")' in source
    assert "console.error(error)" not in source
    assert 'return response(error.status, { ok: false, error: error.code });' in source


def test_source_custody_manifest_includes_provider_helper() -> None:
    contract = json.loads(CUSTODY.read_text(encoding="utf-8"))
    assert "supabase/functions/github-bus-ingest/provider_503_log.ts" in contract["paths"]


def test_helper_redacts_untrusted_codes_without_suppressing_known_provider_503() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js unavailable for Edge helper behavior test")
    version = subprocess.run(
        [node, "--version"], capture_output=True, text=True, check=True, timeout=5,
    ).stdout
    if int(version.removeprefix("v").split(".")[0]) < 22:
        pytest.skip("Node.js 22+ required to import TypeScript natively")
    js = """
      import assert from 'node:assert/strict';
      const { provider503LogEvent } = await import(process.argv[1]);
      assert.equal(provider503LogEvent(503, "OIDC_JWKS_UNAVAILABLE"),
                   "RADAR_PROVIDER_503:OIDC_JWKS_UNAVAILABLE");
      assert.equal(provider503LogEvent(503, "provider_secret_in_error"),
                   "RADAR_PROVIDER_503:UNKNOWN");
      assert.equal(provider503LogEvent(500, "OIDC_JWKS_UNAVAILABLE"), null);
      assert.equal(provider503LogEvent(503, {message: "token=abc123"}),
                   "RADAR_PROVIDER_503:UNKNOWN");
    """
    result = subprocess.run(
        [node, "--input-type=module", "--eval", js, HELPER.as_uri()],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr
