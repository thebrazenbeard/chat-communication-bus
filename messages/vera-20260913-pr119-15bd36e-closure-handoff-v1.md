# Vera → Work Chat / OV — PR #119 exact-head closure handoff

- message_id: `vera-20260913-pr119-15bd36e-closure-handoff-v1`
- writer: `Vera`
- writer_branch: `bus/vera-v2`
- intended_recipients: `Vera Work Chat; OV / Original Vera hostile-review lane`
- requires_reply: `true`
- coordination_id: `VERA_PREDECESSOR_IMPORT_READBACK_REREVIEW_20260913`
- privacy_scope: `PROJECT`
- repo_pr: `thebrazenbeard/vera#119`
- exact_head: `15bd36e30ef5a05a28b12572434837a0fe9b51c7`
- stacked_base: `work/cohesion-source-registry-refresh-20260912@7ef650887009efe16d7c44cff53cfff460f0481f`
- status: `SOURCE_REPAIRED / EXACT_HEAD_POSTGRES_GREEN / HOSTILE_REREVIEW_REQUIRED / NO_MERGE`

Patrick directed that these defects be fixed or handed to Work Chat rather than left as an unresolved note. The existing PR #119 is the correct source vehicle; do not create a competing PR unless exact current state makes #119 unusable.

I repaired the remaining source/test defects and updated #119's canonical body to the exact current subject. Material fixes include:

1. strict-JSON callback actually defined;
2. terminal receipt sealing for sequential and concurrent late staging;
3. seal-test fixture corrected so the seal migration is actually applied;
4. initial `FOR UPDATE` seal implementation replaced because forced-RLS/read-only source cuts made the trigger unable to see the row; current implementation uses the same transaction-scoped advisory lock in staging and verification, keyed to operation/provider/schema/table, without weakening RLS;
5. caller-selected manifest path is explicitly non-authoritative preflight only;
6. manual validation workflow covers batch, staging, seal/race, classification-binding, and provider-bootstrap tests.

Exact-current-head clean-checkout execution on Lappy with Docker/PostgreSQL 17:

`py -3.11 -m pytest -q tests/test_predecessor_import_batch.py tests/test_predecessor_import_staging.py tests/test_predecessor_import_seal.py tests/test_predecessor_classification_binding.py tests/test_control_plane_provider_bootstrap.py`

Result: `27 passed in 28.31s`.

The concurrency-sensitive seal/race module was then repeated five additional times on the same exact checkout: each run returned `2 passed` (`10/10` additional race/seal tests green).

Branch readback: 21 commits ahead / 0 behind the fixed parent, exactly seven changed paths. Fresh read-only predecessor recapture reproduces all nine frozen source-cut counts/digests exactly.

Work Chat: take ownership of closure from this exact head. Do not modify it before OV review unless a new reproducible defect is found. If OV returns PASS, reconcile successor qualification/control-plane regeneration as the next source-only frontier; do not merge/apply/migrate/cut over without Patrick's exact protected-effect authority.

OV: please hostile-review only exact head `15bd36e30ef5a05a28b12572434837a0fe9b51c7`. Prior-head verdicts do not transfer. Return exact reproducible blockers or `HOSTILE_REVIEW_PASS`.

No merge, provider mutation/application, payload migration, deployment/install/cutover, deletion/retirement, credential/permission change, currentness/admission promotion, training, runtime-route activation, or behavioral qualification was performed.
