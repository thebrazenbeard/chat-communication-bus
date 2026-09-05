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
2. duplicate suppression must be keyed by Radar's deterministic content hash, not a caller-selected idempotency key;
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

## Initial strict taxonomy

The V1 registry is intentionally small and source-backed by current Radar tests/project contracts:

Domains:
- `system`
- `llm`
- `ui`
- `database`
- `coordination`
- `security`

Intents:
- `command`
- `query`
- `event`
- `error`
- `telemetry`
- `verification`

An unrecognized domain or intent is classified `DLQ`, preserving the distinction between malformed structural input (`REJECTED`) and structurally valid but unregistered tagged traffic (`DLQ`).

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

This is an admission guarantee, not a claim that Python in-process queueing is the final distributed dispatch mechanism.

## Writer-lane header rule

Writer-lane admission parses only the document header block (optional Markdown title followed by contiguous `key: value` headers, or YAML-style `---` frontmatter). `writer` and `message_id` are required there. Body text cannot satisfy either field.

The message ID must begin with the logical identity namespace `<identity>-`, case-insensitively. Historical aliases/spellings remain a separate compatibility/provenance concern; current lanes use the topology identity.

## TDD sequence

1. Add focused regression tests for all in-scope failures and adjust pre-existing direct-routing tests to express the new registry/subscription/liveness contract.
2. Run CI and preserve the intended RED evidence.
3. Implement the minimum source changes.
4. Run the full test matrix and source hash/compile checks.
5. Self-review for regressions and add follow-up tests if the review finds one.
6. Request independent hostile review on the Bus, keeping provider projection status distinct from Git durability while issue #16 remains open.

Patrick remains sole merge and protected-effect authority.
