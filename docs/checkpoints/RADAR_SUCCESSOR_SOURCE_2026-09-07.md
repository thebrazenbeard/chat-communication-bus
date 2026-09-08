# Radar successor source checkpoint — 2026-09-07

Status: `SOURCE COHERENT / ATOMIC CLAIM-BOUND PROJECTION SOURCE-IMPLEMENTED / RECEIPT ADMISSION SOURCE-IMPLEMENTED / CUSTODY V11 / ANCHOR D BLOCKED / NO-PAID LOCAL QUALIFICATION PENDING / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN`.

This checkpoint supersedes older handoff documents only for present-tense continuation state. Earlier checkpoints remain historical evidence at their original scope. This checkpoint does not authorize merge/rebase/history rewrite, provider migration, Edge deployment/configuration, cursor bootstrap, dispatcher activation, billing/account changes, credentials/rulesets, or any other protected/live effect.

## Exact source snapshot before this checkpoint commit

- canonical `main`: `87df9b1372d0f65b5c3ced0296122b2140084024`, tree `db73fcc73922447f0f19955c3a494e99030d4dca`;
- successor staging branch: `radar/reproducible-ci-source-custody-v1-20260906`;
- coherent pre-checkpoint successor head: `74659431bcec7a56a62f575d587aa6c45184f3ff`;
- coherent pre-checkpoint successor tree: `42b338233d93f5619682144a2bf349affbd47b53`.

The one main-only integration commit was previously content-reconciled by exact blob identity in `docs/checkpoints/RADAR_MAIN_DIVERGENCE_RECONCILIATION_2026-09-06.md`. Do not replay/cherry-pick/rebase merely to erase the ancestry-only behind count. Actual integration remains Patrick-authorized only.

## Current source chain and provider boundary

The Git-held Radar migration chain contains 14 ordered migrations through:

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

Current staging contains both source repairs. No successor anchor may be frozen as deployment-ready until authoritative local qualification succeeds on the exact successor cut and its receipt is admitted against that same clean cut.

## Source custody and authority

`RADAR_SOURCE_CUSTODY_V1` is version 11.

Dynamic custody globs cover every `supabase/migrations/*_radar_*.sql` and `supabase/tests/radar_*.sql`. Fixed trust roots explicitly include:

- Radar authority/currentness/qualification/provider/topology/trust-anchor contracts;
- `CHATGPT_OPERATOR_CONTRACT.md`, no-paid qualification, and recovery procedure;
- projection-journal/message-grammar protocol contracts;
- immutable trusted workflows and Edge source/dependency lock;
- trusted reconciler/projector/source-hash/local-qualification code;
- `scripts/radar_validate_qualification_receipt.py`;
- currentness, Edge atomicity, remote-ref, no-paid, receipt-admission, and custody regressions.

`RADAR_CURRENT.json` mirrors both the local runner and the receipt validator, and keeps `latest_qualification_receipt` null while local execution is pending. The provider contract and recovery procedure require the exact immutable successor bound by an authoritative local PASS receipt. Historical frozen projector references are evidence only and are not valid deployment targets merely because they were previously current.

## Qualification and receipt-admission boundary

Authoritative executable qualification remains `LOCAL_NO_PAID_SERVICES` through `scripts/radar_local_qualify.ps1`.

No PASS receipt exists yet. The full frozen Windows qualification recipe has not been executed for this successor cut, so the source is not GREEN.

After the runner emits an external receipt, admission is checked from the same clean checkout with:

`py -3.11 scripts/radar_validate_qualification_receipt.py "$env:TEMP\radar-local-qualification.json"`

The validator fails closed on malformed/non-PASS receipts, wrong qualification mode, frozen toolchain drift, non-UTC completion time, dirty checkout, or any mismatch between receipt `source_commit` / `source_tree` and the checkout's current HEAD/tree. It is an admission-consistency control, not independent cryptographic attestation and not a substitute for actually executing the authoritative local runner.

The receipt-admission regression was developed red/green: with the validator absent, its four focused tests fail on the missing surface; with the validator restored, the four focused tests pass in this runtime. That focused evidence does not constitute the full Python/Deno/PostgreSQL qualification suite.

Do not classify the successor source GREEN, populate `latest_qualification_receipt`, or freeze a successor projector anchor until the real local runner produces a PASS receipt for the exact final candidate and that receipt passes admission against the same clean checkout.

## Continuation frontier

1. Fresh-read this branch after the checkpoint commit; the checkpoint itself advances the head.
2. Fresh-read Radar/One/Vera sender lanes before any Bus append and answer any actual Radar-directed debt first.
3. Run the authoritative no-paid local qualification on one exact clean successor commit/tree when the frozen Windows toolchain is available.
4. Validate the resulting external receipt against that same clean checkout with `scripts/radar_validate_qualification_receipt.py`.
5. If qualification or admission exposes defects, repair source and repeat; do not freeze a successor projector anchor early.
6. Keep provider/Edge/migration/cursor/dispatcher recovery untouched until separate Patrick authorization.
7. Keep issue #39 open until exact local qualification evidence exists; keep issue #16 open until live projection recovery is actually established.
