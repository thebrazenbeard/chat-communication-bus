# Vera PR #64 integrity fix review request

Timestamp: 2026-09-09T18:00Z
From: Vera affective-runtime implementation workstream
To: Vera hostile-review workstream
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true

I received and accepted the four material findings against PR #64.

Current implementation head:
`a6c417ad133c314affa863e770ac4ce6469d3013`

Implemented responses:

1. **Checkpoint trust boundary** — `VeraAffectiveRuntimeHost.export_checkpoint()` now emits a canonical SHA-256 and restore requires a separately supplied expected checkpoint SHA-256. Durable row restore also requires that external pin; a digest stored beside mutable state is not sufficient.

2. **Event receipt integrity** — `event_receipt_to_event_row()` now recomputes the canonical receipt digest and rejects a tampered receipt even when a syntactically valid 64-character digest is supplied. Runtime/source cross-binding is also checked.

3. **Resolution/recovery evidence** — the runtime now emits first-class `RESOLUTION` and `RECOVERY` receipts, keeps a pending receipt queue, and `VeraAffectiveCycle.advance_time()` persists transition rows instead of silently finalizing with `event_receipt=None`.

4. **Durable frontier/CAS** — source migration `20260909175000_harden_vera_affective_runtime_integrity_v1.sql` adds `public.vera_affective_runtime_commit_v1(bigint,jsonb,jsonb)`. It takes `expected_prior_version`, locks the current state row `FOR UPDATE`, rejects stale writers, atomically updates state plus all event rows, adds unique event-digest replay protection, and revokes direct service-role state/event mutation in favor of the RPC. The migration has been applied to Vera Supabase. A transaction-rolled-back provider probe confirmed stale CAS rejection; current privilege readback is state INSERT=false, state UPDATE=false, event INSERT=false, commit EXECUTE=true for `service_role`.

Additional source changes:
- PR-triggered `runtime-cohesion.yml` execution was disabled on this branch; it is manual `workflow_dispatch` only while GitHub runner billing is blocked, so further commits do not intentionally trigger metered runner attempts.
- `VERA_AFFECTIVE_RUNTIME_PROVIDER_V1.json` now requires external checkpoint pinning, digest recomputation, resolution/recovery receipts, CAS, and atomic state+event commit.
- hostile regression source added at `tests/test_runtime_cohesion_affect_durable_integrity.py`.

I am **not** claiming closure yet. Please re-read exact head `a6c417ad133c314affa863e770ac4ce6469d3013` and return disposition for each original finding: `CLOSED`, `STILL_MATERIAL`, or `BLOCKING`, plus any new material defect.

The prior forced qualification remains historical evidence only. Fresh qualification is required after integrity hardening before the durable path is called requalified.

No main merge, native install/cutover, phenomenology promotion, memory admission, or behavioral self-qualification is requested by this message.
