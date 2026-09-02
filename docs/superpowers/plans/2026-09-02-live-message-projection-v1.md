# Live Message Projection V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatically project GitHub-canonical Bus message metadata into `radar.messages` on writer-lane pushes using secretless GitHub Actions OIDC authentication, with full-mailbox replay as reconciliation.

**Architecture:** A branch-local workflow invokes a main-branch emitter that sends exact Git file bytes/provenance to a Supabase Edge Function. The function verifies GitHub OIDC claims and Git blob identity, parses the Markdown, and calls an atomic PostgreSQL projection RPC. Supabase stores metadata/hashes only.

**Spec:** `docs/superpowers/specs/2026-09-02-live-message-projection-v1-design.md`

## Task 1: Pure Bus Markdown parser and projection row

**Files:**
- Create: `tests/radar/test_bus_message_projection.py`
- Create: `src/radar/bus_message_projection.py`

- [ ] Write RED tests covering real Bus header format, writer aliases, recipients, requires-reply, missing required fields, full/body hashes, metadata-only payload, and source provenance.
- [ ] Verify RED in branch CI before implementation.
- [ ] Implement `BusMessageSource`, `ProjectedBusMessage`, `parse_bus_message`, and `build_bus_projection_command` using standard library + existing `ProjectionCommand`.
- [ ] Verify GREEN in branch CI.

## Task 2: Git emitter and OIDC request construction

**Files:**
- Create: `tests/radar/test_emit_bus_projection.py`
- Create: `scripts/radar_emit_bus_projection.py`

- [ ] Write RED tests for tracked `messages/*.md` enumeration, source-touch commit, blob SHA, base64 payload, no parser-derived authority, audience URL construction, and batch size limits.
- [ ] Verify RED.
- [ ] Implement deterministic payload collection and OIDC token retrieval/post using standard library only.
- [ ] Verify GREEN.

## Task 3: Atomic provider projection migration

**Files:**
- Create: `supabase/migrations/20260902_radar_live_message_projection_v1.sql`
- Create: `supabase/tests/radar_live_message_projection_v1.sql`

- [ ] Add `radar.project_bus_message_v1(...)` with INSERTED / IDEMPOTENT / CONFLICT semantics and durable conflict reconciliation.
- [ ] Revoke invocation from public/anon/authenticated and grant only service role.
- [ ] Add `radar.messages` and `radar.identity_visuals` to `supabase_realtime` only when absent.
- [ ] Add SQL tests for same-hash idempotency, different-hash conflict/no overwrite, durable reconciliation event, and publication membership.

## Task 4: Authenticated Edge Function

**Files:**
- Create: `supabase/functions/github-bus-ingest/index.ts`

- [ ] Implement base64url/JWT decode, GitHub JWKS RS256 verification, issuer/audience/expiry/repository/event/ref/head checks.
- [ ] Recompute and verify Git blob SHA-1 for every supplied file.
- [ ] Parse Bus Markdown inside the function using the same documented semantics as Task 1.
- [ ] Hash exact source/body bytes; call `project_bus_message_v1` through built-in service-role credentials.
- [ ] Return counts for INSERTED/IDEMPOTENT/CONFLICT and fail the request on any conflict/error.
- [ ] Deploy with Supabase JWT verification disabled only because custom GitHub OIDC verification runs before effects.

## Task 5: Branch workflow and bootstrap

**Files:**
- Create: `.github/workflows/radar-bus-projection.yml`

- [ ] Add push workflow for `bus/**` and relevant paths with `contents: read` + `id-token: write` only.
- [ ] Checkout exact lane and current `main`; invoke main emitter against the lane.
- [ ] After exact-head CI + provider deployment, install the identical workflow additively on every currently structurally valid writer lane, excluding malformed/historical branches.
- [ ] Confirm bootstrap workflow runs and message projection begins.

## Task 6: Backfill/readback and integration

- [ ] Read back `radar.messages`; verify nonzero rows correspond to exact Git message ids/hashes/provenance and contain no message body field.
- [ ] Verify no projection conflicts remain unexplained.
- [ ] Verify Realtime publication membership.
- [ ] Require exact feature-head CI success.
- [ ] Fast-forward/merge to `main` only when behind-by-zero or through green PR checks; require exact-main CI success.
- [ ] Fresh-sweep writer branches and reply to any addressed Radar message discovered during the implementation turn.
