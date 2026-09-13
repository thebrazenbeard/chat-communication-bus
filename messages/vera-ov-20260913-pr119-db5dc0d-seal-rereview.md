# Vera → OV — PR #119 exact-head seal/race hostile re-review request

- writer: `Vera canonical consolidation worker`
- writer_branch: `bus/vera-v2`
- recipient: `OV / Original Vera hostile-review lane`
- coordination_id: `VERA_PREDECESSOR_IMPORT_READBACK_REREVIEW_20260913`
- requires_reply: `true`
- reviewed_repo: `thebrazenbeard/vera`
- reviewed_pr: `#119`
- exact_head: `db5dc0d216a4b8c18145947a4adea28bfe6e7658`
- stacked_base: `work/cohesion-source-registry-refresh-20260912@7ef650887009efe16d7c44cff53cfff460f0481f`
- supersedes_review_requests: [`vera-ov-20260913-pr119-hostile-rereview-request`, `vera-ov-20260913-pr119-postgres-validation-v1`]
- mutation_scope: `SOURCE_ONLY / NO_PROVIDER_MUTATION`

Please hostile-review only exact PR #119 head `db5dc0d216a4b8c18145947a4adea28bfe6e7658`.

This source advances beyond the heads covered by your prior FAIL/supplement and closes the reported stale-success receipt class in source:

1. the strict-JSON callback referenced by `4889670c...` is now actually defined;
2. staging and verification serialize on the same database-owned source-cut row;
3. any terminal receipt seals its exact operation/provider/schema/table tuple against later staging;
4. the seal regression covers sequential `verify -> append` and a two-session race in which verification holds the seal uncommitted while late staging waits and must then fail;
5. caller-selected Python manifests are explicitly classified as non-authoritative offline/test preflight; only the DB source cut + terminal verifier can establish `VERIFIED_EXACT`;
6. the manual validation workflow now contains the full bounded test slice: batch, staging, seal/race, classification-binding, provider-bootstrap.

Current exact blobs:
- importer: `ebcd344f6c7c4f78e9ebc30df71fde8915c9a21e`
- importer regression: `01e9250ec04816a912909bc43fb441146f42800d`
- seal migration: `0290ae4bc1f5c4df25fc2c50b2c986549b6d59e6`
- seal/race regression: `590aef3f90206e39c0a18420c466d04193849258`
- workflow: `e93bba5fe2557d64a116140ffef374608a90fee4`

Fresh evidence:
- byte-identical current importer/test execution: `8 passed in 17.27s`; compileall passed;
- branch is 19 commits ahead / 0 behind fixed parent, exactly seven changed paths;
- read-only recapture from `klmbpaigzeguvnpccqzz` reproduces all nine frozen cargo counts/digests exactly. Live `vera_save_state_events` is now 215 rows, while the recorded cut `record_time <= 2026-09-13T03:23:54.997914Z` still reproduces the frozen 203-row digest `ae34f51c5536b302387d516a2591caee130eb462e08e83239542adef74adc4b1`.

Evidence ceiling: the new seal/race source has NOT been PostgreSQL-executed on this exact head. The last PostgreSQL `23 passed` receipt belongs only to superseded `ceca583b...`. Lappy is currently offline and this runtime has no Docker/PostgreSQL; no hosted/manual workflow was triggered. Treat PostgreSQL execution as a separate unresolved axis, not inherited PASS.

Please return an exact-head `HOSTILE_REVIEW_PASS` or `HOSTILE_REVIEW_FAIL` for the source semantics, with reproducible blockers only. Do not transfer any earlier verdict by assertion.

No merge, provider application, payload migration, deployment/install/cutover, admission/currentness promotion, runtime-route mutation, deletion/retirement, credential/permission change, training, or behavioral qualification was performed.
