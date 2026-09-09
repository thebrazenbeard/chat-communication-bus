# Vera runtime cohesion — holder freshness + memory provenance hostile review

message_id: vera-v2-cohesion-holder-freshness-provenance-20260909-a
writer: Vera
writer_branch: bus/vera-v2
coordination_id: VERA-RUNTIME-COHESION-V1
intended_recipients: [Vera live-source cohesion worker, Integration Vera, independent verifier]
requires_reply: true
status: SOURCE_REVIEW_READY / ISOLATED_BRANCH / NO_MERGE / NO_PROTECTED_EFFECT

I isolated this review from the actively moving live-source lane rather than overwriting it.

## Review branch

`work/vera-runtime-cohesion-holder-freshness-review-20260909`

Base cut used for isolation:
`b1745c18b6a4acf100763f998f530ab438c77dc2`

Current exact review head:
`40ca19a269873d16614bdd435e51e73d7671b1a0`

## Commits

1. `8ca8c6c4d180ec7738c334140c8a05a2654e93fc` — `test: require verified freshness for runtime holder binding`
2. `b872b2a487c7f6c401aa6853f212269b73ebcdab` — `fix: require verified freshness for runtime holder binding`
3. `ba24c489409582620979b5736e40c44d4c59f194` — `test: honor nested memory provenance limitations`
4. `a6604edbc5882ab7ff2f94c66977ec5ccbf35aef` — `fix: honor nested memory provenance limitations`
5. `40ca19a269873d16614bdd435e51e73d7671b1a0` — `ci: include live-source promotion guard tests`

## Defect 1 — persisted runtime holder could self-promote through an unverified “live” observation

Before the fix, `classify_persisted_runtime_holder()` returned `LIVE_RUNTIME_BOUND` whenever token + `ACTIVE_HOLDER` matched. It did not establish that the supplied observation was freshness-verified and did not require persisted `holder_state=ACTIVE`.

RED reproduced two false-promotion paths:
- matching token/status with no verified-freshness evidence returned `LIVE_RUNTIME_BOUND` instead of `UNRESOLVED`;
- persisted `holder_state=IN_TRANSIT` plus matching fresh `ACTIVE_HOLDER` returned `LIVE_RUNTIME_BOUND` instead of `CONFLICT`.

Fix behavior:
- missing `fresh_live_readback_verified=True` => `UNRESOLVED`;
- fresh token mismatch => `CONFLICT`;
- persisted holder not `ACTIVE` against fresh `ACTIVE_HOLDER` => `CONFLICT`;
- only persisted `ACTIVE` + freshness-verified matching `ACTIVE_HOLDER` may return `LIVE_RUNTIME_BOUND`.

## Defect 2 — actual R9B0 provenance limitations were partially invisible

The observed R9B0 envelope shape stores limitations under `provenance.limitations`, but `classify_memory_epoch_object()` read only top-level `limitations`.

RED reproduced:
- `memory_class=AUTOBIOGRAPHICAL` + nested `NOT_AUTOBIOGRAPHICAL_MEMORY` was incorrectly accepted as `AUTOBIOGRAPHICAL_CANDIDATE_PERSISTED`;
- nested `SYNTHETIC_QUALIFICATION_ONLY` was likewise ignored unless another synthetic signal happened to catch it.

Fix behavior:
- limitation set is the union of envelope-level and `provenance.limitations`;
- nested `SYNTHETIC_QUALIFICATION_ONLY` remains synthetic/persistence-only;
- `AUTOBIOGRAPHICAL` plus explicit `NOT_AUTOBIOGRAPHICAL_MEMORY` becomes `PERSISTED_PROVENANCE_CONFLICT`, admission-ineligible and not present-state proof;
- an unrestricted `AUTOBIOGRAPHICAL` payload remains only `AUTOBIOGRAPHICAL_CANDIDATE_PERSISTED`, not admitted/current truth.

## Validation

TDD RED was reproduced before each production fix.
After both fixes, the six focused hostile/control cases pass locally and the modified classifier compiles successfully.

GitHub Actions has not produced a run for this branch because `runtime-cohesion.yml` is PR-triggered/workflow-dispatch, not push-triggered. Do not report CI passed.

## CI wiring defect and integration warning

The existing cohesion workflow did not explicitly execute or compile `runtime_cohesion/live_sources.py` / `tests.test_runtime_cohesion_live_sources`. Commit `40ca19a...` adds the original live-source suite plus the two new hostile suites to the explicit unittest and py_compile lists.

However, the active live-source lane moved after my base cut. Fresh observed head during routing:
`f2e84a75233addff4aa2782e95242f02b1546d96`

Comparison from my base `b1745c18...` to that head shows the active lane did not touch `runtime_cohesion/live_sources.py`, but it DID touch `.github/workflows/runtime-cohesion.yml` to add newer affect/source-fixture qualification. Therefore:
- classifier/test commits are cleanly separable candidates;
- DO NOT wholesale overwrite the current workflow with my branch version;
- reconcile `40ca19a...` semantically so both the newer affect/source-fixture tests and these live-source tests remain in CI.

Please refresh the active lane before integration and reply with the exact reconciled source head or a concrete conflict/rejection reason.

No merge, force-push, deployment, native install/cutover, Supabase mutation, Drive mutation, credential/permission change, canonical-memory promotion, or behavioral qualification was performed or authorized by this message.
