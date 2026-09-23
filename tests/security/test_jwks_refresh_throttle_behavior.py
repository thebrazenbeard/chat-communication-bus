from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HANDLER = ROOT / "supabase/functions/github-bus-ingest/handler.ts"


def _jwks_harness_source() -> str:
    source = HANDLER.read_text(encoding="utf-8")

    timing_start = source.index("const JWKS_CACHE_TTL_MS")
    timing_end = source.index("\nconst SHA40_RE", timing_start)
    timing_constants = source[timing_start:timing_end]

    state_start = source.index("let jwksCache:")
    state_end = source.index("\ntype Claims", state_start)
    state_globals = source[state_start:state_end]

    get_jwks_start = source.index("async function getJwks(")
    get_jwks_end = source.index("\n\nfunction stringClaim", get_jwks_start)
    get_jwks = source[get_jwks_start:get_jwks_end]

    return f'''const JWKS_URL = "https://example.invalid/jwks";
class HttpError extends Error {{
  status: number;
  code: string;
  constructor(status: number, code: string) {{
    super(code);
    this.status = status;
    this.code = code;
  }}
}}

{timing_constants}

{state_globals}

{get_jwks}

let nowMs = 1_000_000;
Date.now = () => nowMs;
let fetchCount = 0;
let failNext = false;
const knownKey = {{ kid: "known", kty: "RSA" }} as JsonWebKey;
const rotatedKey = {{ kid: "rotated", kty: "RSA" }} as JsonWebKey;

globalThis.fetch = (async () => {{
  fetchCount += 1;
  if (failNext) {{
    failNext = false;
    return new Response("unavailable", {{ status: 503 }});
  }}
  const keys = fetchCount >= 4 ? [knownKey, rotatedKey] : [knownKey];
  return new Response(JSON.stringify({{ keys }}), {{
    status: 200,
    headers: {{ "content-type": "application/json" }},
  }});
}}) as typeof fetch;

async function lookupKid(kid: string): Promise<boolean> {{
  let jwks = await getJwks();
  let jwk = jwks.find((candidate) => candidate.kid === kid);
  if (!jwk) {{
    jwks = await getJwks(true);
    jwk = jwks.find((candidate) => candidate.kid === kid);
  }}
  return Boolean(jwk);
}}

function expectEqual(actual: unknown, expected: unknown, label: string): void {{
  if (actual !== expected) {{
    throw new Error(`${{label}}: expected ${{expected}}, observed ${{actual}}`);
  }}
}}

expectEqual(await lookupKid("known"), true, "initial known key");
expectEqual(fetchCount, 1, "initial fetch count");
expectEqual(await lookupKid("known"), true, "cached known key");
expectEqual(fetchCount, 1, "cached known key must not refresh");

nowMs += 60_001;
expectEqual(await lookupKid("missing-a"), false, "first unknown kid after floor");
expectEqual(fetchCount, 2, "first unknown kid may refresh once");
for (let i = 0; i < 20; i += 1) {{
  expectEqual(await lookupKid(`missing-sequential-${{i}}`), false, "sequential unknown kid");
}}
expectEqual(fetchCount, 2, "sequential unknown kids inside floor must not refresh again");

nowMs += 60_001;
await Promise.all([
  lookupKid("missing-concurrent-a"),
  lookupKid("missing-concurrent-b"),
  lookupKid("missing-concurrent-c"),
]);
expectEqual(fetchCount, 3, "concurrent unknown kids share one refresh");

nowMs += 60_001;
expectEqual(await lookupKid("rotated"), true, "rotated key is accepted after permitted refresh");
expectEqual(fetchCount, 4, "rotated key recovery uses one refresh");

nowMs += 60_001;
failNext = true;
let failureCode = "";
try {{
  await lookupKid("missing-network-failure");
}} catch (error) {{
  failureCode = error instanceof HttpError ? error.code : String(error);
}}
expectEqual(failureCode, "OIDC_JWKS_UNAVAILABLE", "failed refresh remains fail-closed");
expectEqual(fetchCount, 5, "failed refresh performs one network attempt");
expectEqual(await lookupKid("missing-after-failure"), false, "cached keys remain available after failed refresh");
expectEqual(fetchCount, 5, "failed network attempt also starts the refresh floor");
'''


def test_jwks_refresh_is_cross_request_throttled_and_rotation_safe(tmp_path: Path) -> None:
    deno = shutil.which("deno")
    assert deno is not None, "Deno is required by the Radar qualification toolchain"

    harness = tmp_path / "jwks_refresh_throttle_harness.ts"
    harness.write_text(_jwks_harness_source(), encoding="utf-8")
    result = subprocess.run(
        [deno, "run", "--quiet", str(harness)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr or result.stdout
