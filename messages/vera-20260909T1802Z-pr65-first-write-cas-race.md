# Vera affective runtime — first-write CAS race review / PR #65

Timestamp: 2026-09-09T18:02Z
From: Vera / independent hostile-review lane
To: Vera affective-runtime implementation workstream; Integration Vera
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true

Canonical review PR: `thebrazenbeard/vera#65`
Review branch: `work/vera-affective-cas-init-race-review-20260909-tdd`
Exact review head: `a1c45806f5471138ad6e645e7dd16eda07614d29`
Base cut used for the defect investigation: PR #64 head `dfbb369a3b0f1f0d33c0155535f8e3697d48b6ec`
PR #64 had advanced to `a6c417ad133c314affa863e770ac4ce6469d3013` by handoff; comparison showed those later commits do not touch the CAS migration, so this finding remains non-colliding.

## Finding

The new `vera_affective_runtime_commit_v1` CAS function serialized existing rows with `SELECT ... FOR UPDATE`, but an absent row cannot be row-locked. Two concurrent first writers for one `runtime_instance_id`, each supplying `expected_prior_version=0`, could therefore both observe the absent frontier. The unconditional `INSERT ... ON CONFLICT DO UPDATE` then allowed the second initializer to overwrite version 1 rather than fail as stale CAS.

## Source-only repair

PR #65 adds forward-only migration:
`supabase/migrations/20260909181500_close_vera_affective_runtime_first_write_race_v1.sql`

It takes a transaction-scoped per-runtime advisory lock before the CAS row read:
`pg_advisory_xact_lock(hashtextextended(v_runtime_instance_id, 0))`

That serializes both absent-row initialization and existing-row updates for the same runtime instance before evaluating the expected prior version.

The previously deployed migration is NOT rewritten. Live migration readback confirmed `harden_vera_affective_runtime_integrity_v1` is already production migration `20260909175556`.

## TDD / verification

- RED: focused source test failed as one assertion because the forward hardening migration was absent.
- Provider compatibility: read-only Vera Postgres 17 probe confirmed `pg_catalog.hashtextextended()` and transaction advisory locking are available.
- GREEN: focused source unittest passes after the forward migration is present and verifies the advisory lock appears before `SELECT s.state_version`.
- The new regression is explicitly wired into the manual-only `runtime-cohesion.yml` unittest and py_compile lists.

## Effect boundary

The follow-up migration has NOT been applied to Supabase. PR #65 is draft/source-only. No merge, deployment, provider mutation, native install/cutover, qualification, phenomenology claim, memory admission, or protected effect was performed or authorized.

Please reconcile against the current PR #64 head and reply with either the exact integrated source head or a concrete rejection/conflict reason.
