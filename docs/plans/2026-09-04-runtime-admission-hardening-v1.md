# Radar runtime admission hardening V1

Date: 2026-09-04
Base: `main@b2950bcb547fb78d16e44cd94a6ba2164937bf44`
Branch: `radar/runtime-admission-hardening-v1-20260904`

## Purpose

Convert the bounded, source-local failures from Draft PR #17 into fail-closed runtime behavior without mixing them with the larger projector trust-root redesign or the live Supabase recovery incident.

This branch is intentionally source-only. It does not merge, deploy, change credentials/rulesets, mutate provider state, rewrite historical messages, or alter protected effects.

## Scope

This pass owns the source-local portions of the red-team findings:

1. unknown domain / intent tags must fail closed into `DLQ`;
2. duplicate suppression must use the `deterministic_hash` semantics of the supplied Radar middleware draft rather than caller-selected idempotency keys;
3. priority `0` admission must not be blocked merely because a bounded queue is saturated with lower-urgency background work;
4. explicit audience routing must not bypass domain subscription authorization;
5. subscription/direct routing must not dispatch to an identity with no currently routable registered node;
6. a current writer-lane message must contain a top-level `writer:` header;
7. a current writer-lane message must contain a top-level `message_id:` header;
8. a body-only `writer:` marker must not satisfy the writer-lane guard;
9. a writer lane must not claim another logical identity's message-ID namespace;
10. provider per-file `CONFLICT` results must make the emitter fail visibly.

## Deliberately separate

These remain outside this branch because they require a different release boundary or transport contract:

- full-mailbox projection exceeding the Edge 500-file limit: solve with exact-delta/chunked projection rather than silent truncation;
- trusted projector root / `job_workflow_ref` binding;
- provider sender derivation from authenticated lane identity;
- independent proof that source commit/path/blob are reachable from the authenticated Git head;
- live `github-bus-ingest` v3 recovery (`verify_jwt` gateway mismatch);
- the 60-second Radar heartbeat and routed/dropped/DLQ telemetry, which deserve a dedicated telemetry slice after admission semantics are stable.

## Strict taxonomy

The registry is intentionally hardcoded, but it must also be compatible with source-backed and provider-observed values already in use. A self-review against the live read-only Radar projection caught an initial under-specified allowlist before promotion: 216 projected messages currently use `domain=chat_bus`, `intent=bus_message`, and current subscriptions also use `protocol` and `repository`. Those values are therefore part of the admitted V1 taxonomy rather than being silently dead-lettered.

Domains:
- `system`
- `llm`
- `ui`
- `database`
- `coordination`
- `security`
- `chat_bus`
- `protocol`
- `repository`

Intents:
- `command`
- `query`
- `event`
- `error`
- `telemetry`
- `verification`
- `bus_message`

An unrecognized domain or intent is classified `DLQ`, preserving the distinction between malformed structural input (`REJECTED`) and structurally valid but unregistered tagged traffic (`DLQ`).

## Deterministic duplicate hash

The supplied `radar_middleware_draft.py` computes `deterministic_hash` as SHA-256 of `json.dumps(payload, sort_keys=True)`. The hardened envelope therefore keeps two separate hashes:

- `content_hash`: provenance/content identity over sender + audience + domain + intent + payload;
- `idempotency_key`: Radar-owned duplicate key using the middleware's payload-only deterministic hash.

Caller-supplied `idempotency_key` is non-authoritative. Non-JSON payloads fail closed before hashing so the implementation cannot silently invent process-specific string representations that differ from the supplied middleware contract.

This preserves the explicitly supplied middleware behavior instead of conflating provenance identity with the 500 ms duplicate window.

## Routing/liveness rule

A recipient is routable only when all applicable authorization checks succeed and the logical identity has at least one registered node in a routable state.

Routable states for V1:
- `ONLINE`
- `IDLE`
- `WORKING`
- `WAITING_DEPENDENCY`
- `DEGRADED`

Non-routable:
- `OFFLINE`
- `PAUSED`
- `ARCHIVED`

Explicit audience does not grant authorization by itself: the named identity must also hold a matching domain subscription at the message priority and have a routable node.

## Priority-0 saturation rule

When the bounded queue is full, a priority-0 message may evict one queued lower-urgency item. Eviction is deterministic: choose the least urgent numeric priority first, and for equal priority evict the most recently admitted item. If the queue is already entirely priority 0, fail with `RADAR_QUEUE_FULL` rather than silently discarding a halt/security-class message.

This is an admission guarantee, not a claim that Python in-process queueing is the final distributed dispatch mechanism. Eviction accounting must be exposed by the later telemetry/heartbeat slice so dropped background work does not become invisible.

## Writer-lane header rule

Writer-lane admission parses only the document header block (optional Markdown title followed by contiguous `key: value` headers, or YAML-style `---` frontmatter). `writer` and `message_id` are required there. Body text cannot satisfy either field.

The message ID must begin with the logical identity namespace `<identity>-`, case-insensitively. Historical aliases/spellings remain a separate compatibility/provenance concern; current lanes use the topology identity.

## TDD evidence sequence

1. Initial focused regression set produced the intended RED result: 10 failures with 177 existing tests passing.
2. The first implementation pass produced 187/187 green on Python 3.11 and 3.12, including compile and source-hash checks.
3. Live read-only taxonomy reconciliation then exposed three compatibility defects in the first allowlist (`chat_bus`, `bus_message`, `protocol`, `repository`), and a focused compatibility test reproduced them as 3 failures with 191 tests passing.
4. A separate source check against the supplied middleware draft showed that its deterministic duplicate hash is payload-only, not the broader provenance `content_hash`; a focused test reproduced that mismatch.
5. A fail-closed JSON-serialization test then isolated the remaining middleware-compatibility edge: after correcting the stale hash assertion, the exact RED result was 1 failure with 195 tests passing.
6. Implementation head `a1a59fb5e3a9e4172488d8efd32f842a564eea6f` then passed 196/196 tests on Python 3.11 and 3.12, with compile and source-hash checks green.
7. The documentation-only evidence update that follows that implementation head still requires one final exact-head CI readback before review-ready status is claimed.
8. Request independent hostile review on the Bus, keeping provider projection status distinct from Git durability while issue #16 remains open.

Patrick remains sole merge and protected-effect authority.
