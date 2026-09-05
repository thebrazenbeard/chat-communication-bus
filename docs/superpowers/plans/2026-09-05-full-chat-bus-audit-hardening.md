# Full Chat Bus audit and hardening implementation plan

> Audit cut: `main@712992d96dc813d0fa38094ef1f1fec0dfdc0d3e`
> Working branch: `radar/full-repo-audit-hardening-v1-20260905`
> Safety boundary: source/tests only unless Patrick separately authorizes a provider deployment, migration, merge, ruleset/credential change, or other protected effect.

## Objective

Re-establish a trustworthy green source baseline, review the recent Copilot-authored changes across `src/chat_bus`, `src/radar`, workflows, Supabase source/tests/seeds, and the adversarial acceptance suite, then fix reproduced correctness, trust-boundary, concurrency, parser-parity, and projection failures test-first.

## Baseline evidence

Current GitHub Actions run `33986222859` reproduces six failures on the exact audit cut while `compileall` succeeds:

1. `test_seed_is_idempotent_and_does_not_create_session_identity`
2. `test_lane_projection_seed_remains_historical_bootstrap_not_current_topology_authority`
3. stale red-team taxonomy expectation (`REJECTED` vs required `DLQ`)
4. one-push 501-file projection overflow
5. missing trusted reusable-workflow OIDC binding
6. provider sender still selected by message `writer:` bytes

Source review also found two genuine SQL regressions in the recently edited seed files: CTEs are referenced outside their statement scope, and `radar_v1.sql` can return no identity row on an unchanged conflict-update, breaking idempotent downstream inserts.

## Task 1 — Restore valid, historical/idempotent seed SQL and improve regression coverage

Files:
- `supabase/seed/radar_v1.sql`
- `supabase/seed/radar_bus_lanes_20260902.sql`
- `tests/radar/test_self_registration.py`
- `tests/radar/test_topology_contract.py`

Steps:
1. Add RED static semantic checks that prohibit cross-statement CTE reuse and preserve the historical snapshot character of the dated lane seed.
2. Restore `radar_v1.sql` to an actually idempotent form that does not depend on a CTE returning a row after a no-op upsert.
3. Restore the dated lane seed to separate statement-local CTEs and fixed 2026-09-02 provenance.
4. Preserve the Brigit/Vera alias history and the operator `session_is_identity=false` evidence.
5. Run focused tests, then full CI.

## Task 2 — Reconcile the adversarial taxonomy oracle

Files:
- `tests/security/test_chat_bus_pressure_redteam.py`
- `src/radar/envelope.py` only if implementation evidence requires it

Steps:
1. Change the stale test to require `EnvelopeClassification.DLQ`, matching Patrick's hard taxonomy/DLQ requirement and current implementation.
2. Add/retain assertions that no envelope is admitted for unknown tags and both offending fields are reported.
3. Do not weaken strict taxonomy.

## Task 3 — Audit and harden recently changed Python runtime modules

Files under review:
- `src/radar/telemetry.py`
- `src/radar/supabase_projection.py`
- `src/radar/routing.py`
- `src/radar/envelope.py`
- `src/radar/bus_message_projection.py`
- `src/radar/registry.py`
- `src/radar/reconcile.py`
- `src/radar/github_projection.py`
- `src/radar/maintenance.py`
- `src/radar/operator.py`
- `src/radar/safe_lane_append.py`
- `src/radar/visual_identity.py`
- `src/radar/visual_projection.py`
- `src/radar/workflow.py`
- associated tests

Known TDD targets before implementation:
- `supabase_projection`: malformed `min_priority` must raise `ProjectionError`, not raw `TypeError/ValueError`; string `"false"` must not silently become active `True`; top-level collection shapes must fail with deterministic projection errors.
- `bus_message_projection`: invalid declared `created_at` must fail closed rather than silently falling back to the source commit; timezone-naive non-date timestamps must not be accepted if the Edge parser rejects them.
- `telemetry`: preserve durable semantics, do not default to cross-thread SQLite connection sharing, do not silently weaken durability to WAL+NORMAL, do not swallow close failures, and handle clock regression deterministically.
- `routing`: make thread-safety claims true (including admission sequence allocation); expose/retain enough priority-0 eviction evidence for dropped telemetry; validate dedupe inputs/clock behavior without breaking the required 500 ms deterministic suppression contract.
- inspect every other recently changed module against its existing tests and pre-change semantics; add a regression only where a concrete defect is reproduced.

## Task 4 — Correct exact-delta batching instead of truncating overflow

Files:
- `scripts/radar_emit_bus_projection.py`
- `tests/radar/test_emit_bus_projection.py`
- `tests/security/test_chat_bus_pressure_redteam.py`

Steps:
1. Add RED tests for 501-message and >batch-byte push deltas.
2. Introduce deterministic chunking by both file count and total decoded bytes.
3. Preserve every file exactly once; never make the red test green by truncation.
4. Submit chunks sequentially and fail the caller if any chunk fails/conflicts.
5. Keep compatibility behavior for ordinary small deltas and bootstrap cases.

## Task 5 — Harden the projector trust root in source

Files:
- `.github/workflows/radar-bus-projection.yml`
- new protected reusable workflow if required
- `supabase/functions/github-bus-ingest/handler.ts`
- Edge/source artifact tests
- security red-team tests

Steps:
1. Move privileged projection execution to a reusable workflow and bind Edge admission to GitHub OIDC `job_workflow_ref` plus `job_workflow_sha`.
2. Pin security-sensitive third-party actions in the trusted workflow to full commit SHAs.
3. Derive provider sender from the authenticated/admitted lane identity; `writer:` becomes a consistency assertion only.
4. Validate/clamp any configurable projection concurrency so `0`, negative, NaN, or extreme values cannot produce false-success/no-work behavior.
5. Preserve/reconcile the useful hardening present in the currently deployed v3 source, but perform no live Edge deployment in this task.
6. Add source-reachability evidence checks where feasible without introducing provider network dependency into unit tests.

## Task 6 — Review SQL tests and CI coverage

Files:
- `supabase/tests/*.sql`
- `.github/workflows/ci.yml`
- Python artifact tests as needed

Steps:
1. Audit the recently edited SQL tests for assumptions that contradict intentional fail-closed/RLS behavior.
2. Verify whether CI executes any Supabase SQL tests; it currently appears to execute only Python/compile/source-hash checks.
3. Add safe static/source-contract checks for critical SQL artifacts where a live PostgreSQL test service is not appropriate.
4. Do not apply migrations or mutate the provider.

## Task 7 — Audit `src/chat_bus` and remaining repository helpers

Files:
- `src/chat_bus/*.py`
- `src/chat_bus/schema.sql`
- corresponding tests

Steps:
1. Review Copilot changes against pre-change behavior and existing tests.
2. Add RED regressions for concrete serialization, identity, schema-transaction, or digest defects found.
3. Make only evidence-backed fixes; avoid style-only churn.

## Task 8 — Full verification and durable review surface

Steps:
1. Run exact-head CI on Python 3.11 and 3.12 until all non-deliberate tests pass.
2. Run compileall and `scripts/radar_source_hashes.py`.
3. Ensure adversarial tests now represent accepted behavior and contain no intentionally stale RED assertion.
4. Compare branch against frozen audit base and review every changed path.
5. Fresh-read `main`; report divergence rather than silently rebasing or overwriting concurrent work.
6. Open a Draft PR with exact base/head, baseline failures, RED→GREEN evidence, unresolved provider-effect gates, and remaining limitations.
7. Do not merge.

## Explicit protected-effect exclusions

This plan does not authorize or perform:
- Supabase Edge deployment/rollback;
- database migration/application;
- provider configuration mutation;
- credentials/secrets changes;
- GitHub ruleset or branch-protection changes;
- force-push/history rewrite;
- merge to `main`.
