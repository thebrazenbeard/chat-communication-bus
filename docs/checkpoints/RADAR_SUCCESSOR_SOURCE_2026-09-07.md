# Radar successor source checkpoint — 2026-09-07

Status: `SOURCE COHERENT / ATOMIC CLAIM-BOUND PROJECTION SOURCE-IMPLEMENTED / CUSTODY V10 / ANCHOR D BLOCKED / NO-PAID LOCAL QUALIFICATION PENDING / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN`.

This checkpoint supersedes older handoff documents only for present-tense continuation state. Earlier checkpoints remain historical evidence at their original scope. This checkpoint does not authorize merge/rebase/history rewrite, provider migration, Edge deployment/configuration, cursor bootstrap, dispatcher activation, billing/account changes, credentials/rulesets, or any other protected/live effect.

## Exact source snapshot before this checkpoint commit

- canonical `main`: `87df9b1372d0f65b5c3ced0296122b2140084024`, tree `db73fcc73922447f0f19955c3a494e99030d4dca`;
- successor staging branch: `radar/reproducible-ci-source-custody-v1-20260906`;
- coherent pre-checkpoint successor head: `8f0fecb760ae54f102b09a65b7c76c57a6864a15`;
- coherent pre-checkpoint successor tree: `e5843f8dc12783331149c5af9c5125f77379e72b`;
- compare to `main`: `diverged`, ahead 185, behind 1, merge base `b1c0ceb80c6ce895927cd715319257b28124d919`.

The one main-only integration commit is already content-reconciled by exact blob identity in `docs/checkpoints/RADAR_MAIN_DIVERGENCE_RECONCILIATION_2026-09-06.md`. Do not replay/cherry-pick/rebase merely to erase the ancestry-only behind count. Actual integration remains Patrick-authorized only.

## Current source chain and provider boundary

The Git-held Radar migration chain now contains 14 ordered migrations through:

`20260908010500_radar_projection_atomic_file_v1.sql`

The last recorded provider readback is dated 2026-09-06 and reaches only:

`20260903113314_radar_operator_views_v1`

Therefore six current source migrations are unapplied relative to that recorded provider state: thread closure, OIDC replay guard, node-routing hardening, projection journal, journal API, and atomic claim-bound file projection.

The recorded live `github-bus-ingest` state remains v3 / ACTIVE / `verify_jwt=true`. Current body-bound Edge source, journal/atomic provider objects, projection cursors, and a qualified successor projector SHA are not established as live. Issue #16 remains open.

## Atomic projection repair

The previous projection path could mutate `radar.messages` through the standalone message RPC before the separate journal-result RPC proved the batch claim/path remained current. A stale or expired claim therefore had a source-level path to an unjournaled provider mutation.

Current successor source closes that seam:

- `20260908010500_radar_projection_atomic_file_v1.sql` adds `radar.projection_project_file_v1` plus the service-role public bridge;
- claim-sensitive lock order is normalized as `lane -> batch -> file`;
- active claim token/lease, expected cursor, control/topology cut, exact claimed path, sender identity, source path, and target branch head are validated before message projection;
- provider message projection and terminal file-journal state occur in one SQL transaction;
- unknown projection results fail the transaction closed;
- service-role execution of the legacy standalone message-projection and standalone file-result RPCs is revoked;
- Edge `projectFile()` now calls only `radar_projection_project_file_v1` for the file mutation/journal effect;
- rollback SQL assertions cover expired claim, wrong path, successful atomic projection, idempotent retry, cursor finalize, and ACL bypass prevention.

These are source/contract facts. PostgreSQL/Supabase execution of the new migration/assertions has not occurred in this runtime.

## Projection anchor status

The latest frozen reference remains projection Anchor D:

- commit `401733b2013802880320629a4d8ea06f8bf7b760`;
- tree `d3a9c44f0378409a626e29334b4d057ef20c7e8e`.

It is explicitly NOT deployment-eligible. It predates at least two known required successor repairs:

1. the Python `project_batch` request must include Edge-required `identity` and `branch` fields;
2. file projection/journaling must be atomic and claim-bound.

Current staging contains both repairs. No successor anchor may be frozen as deployment-ready until authoritative local qualification succeeds on the exact successor cut.

## Source custody and authority

`RADAR_SOURCE_CUSTODY_V1` is version 10.

Dynamic custody globs cover every `supabase/migrations/*_radar_*.sql` and `supabase/tests/radar_*.sql`. Fixed trust roots now explicitly include:

- Radar authority/currentness/qualification/provider/topology/trust-anchor contracts;
- `CHATGPT_OPERATOR_CONTRACT.md`, no-paid qualification, and recovery procedure;
- projection-journal/message-grammar protocol contracts;
- immutable trusted workflows and Edge source/dependency lock;
- trusted reconciler/projector/source-hash/local-qualification code;
- currentness, Edge atomicity, remote-ref, no-paid, and custody regressions.

The provider contract and recovery procedure now require the exact immutable successor bound by an authoritative local PASS receipt. Historical frozen projector references are evidence only and are not valid deployment targets merely because they were previously current.

## Qualification boundary

Authoritative qualification remains `LOCAL_NO_PAID_SERVICES` through `scripts/radar_local_qualify.ps1`.

No PASS receipt exists yet. The current runtime does not provide PowerShell, Deno, Supabase CLI, Docker, or `psql`, so it cannot execute the frozen end-to-end qualification recipe here. Fresh committed-byte/source-contract readbacks are useful evidence but are not a substitute for the required local Windows qualification.

Do not classify the successor source GREEN until a clean exact commit/tree receives the required PASS receipt.

## Continuation frontier

1. Fresh-read this branch after the checkpoint commit; the checkpoint itself advances the head.
2. Fresh-read Radar/One/Vera sender lanes before any Bus append and answer any actual Radar-directed debt first.
3. Run the authoritative no-paid local qualification on one exact clean successor commit/tree when the frozen Windows toolchain is available.
4. If qualification exposes defects, repair source and repeat qualification; do not freeze a successor projector anchor early.
5. Keep provider/Edge/migration/cursor/dispatcher recovery untouched until separate Patrick authorization.
6. Keep issue #39 open until exact local qualification evidence exists; keep issue #16 open until live projection recovery is actually established.
