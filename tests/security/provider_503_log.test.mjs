import assert from "node:assert/strict";
import test from "node:test";

import { provider503LogEvent } from "../../supabase/functions/github-bus-ingest/provider_503_log.ts";

const ALLOWED = [
  "OIDC_JWKS_UNAVAILABLE",
  "OIDC_JWKS_INVALID",
  "TRUSTED_PROJECTOR_SHA_INVALID",
  "PROJECT_CONCURRENCY_INVALID",
  "PROVIDER_CONFIGURATION_MISSING",
];

test("only handled provider 503 emits an error diagnostic", () => {
  for (const status of [200, 401, 404, 500, "503", null, undefined, Number.NaN]) {
    assert.equal(provider503LogEvent(status, ALLOWED[0]), null);
  }
});

test("exact approved provider codes pass through on 503", () => {
  for (const code of ALLOWED) {
    assert.equal(provider503LogEvent(503, code), `RADAR_PROVIDER_503:${code}`);
  }
});

test("unknown and injected details are reduced to a fixed label", () => {
  for (const code of [
    "SECRET_KEY=hidden",
    "OIDC_JWKS_INVALID\nsecret",
    "oidc_jwks_invalid",
    " OIDC_JWKS_INVALID ",
    "OIDC_JWKS_INVALID\u200b",
    123,
    null,
    undefined,
    Symbol("sensitive"),
    [ALLOWED[0]],
  ]) {
    assert.equal(provider503LogEvent(503, code), "RADAR_PROVIDER_503:UNKNOWN");
  }
});

test("object conversion hooks and proxy traps are never invoked", () => {
  let traps = 0;
  const hostile = new Proxy({
    toString() { traps += 1; throw Error("secret"); },
  }, {
    get(target, property) { traps += 1; return target[property]; },
  });
  assert.equal(provider503LogEvent(503, hostile), "RADAR_PROVIDER_503:UNKNOWN");
  assert.equal(traps, 0);
});
