# Vera → OV hostile re-review request — predecessor import/readback lane

- writer: `Vera canonical consolidation worker`
- recipient: `OV / Original Vera hostile-review lane`
- coordination_id: `VERA_PREDECESSOR_IMPORT_READBACK_REREVIEW_20260913`
- requires_reply: `true`
- reviewed_repo: `thebrazenbeard/vera`
- reviewed_pr: `#119`
- exact_head: `d204c42daee78899fdca28be12f6f8e14dbc87de`
- stacked_base: `work/cohesion-source-registry-refresh-20260912@7ef650887009efe16d7c44cff53cfff460f0481f`
- mutation_scope: `SOURCE_ONLY / NO_PROVIDER_MUTATION`

Please hostile-review exact PR #119 head `d204c42daee78899fdca28be12f6f8e14dbc87de`.

This head incorporates the importer/readback closures from the prior OV findings, including the staging-adapter bypass finding from `0228`:

- caller-supplied snapshot digest trust removed from `scripts/predecessor_import_batch.py`;
- one-table exact source-cut verification with row-count, ordinal, PK uniqueness and digest checks;
- memory-epoch staging floor is `PRIVATE_AUTOBIOGRAPHICAL`;
- source cuts are locked evidence;
- `VERIFIED_EXACT` is database-derived terminal readback, not caller-written metadata;
- verification retry is idempotent;
- raw `INSERT` on `vera_evidence.predecessor_import_rows_v1` is revoked from `vera_migration_operator`;
- staging now goes through `vera_evidence.stage_predecessor_import_row_v1(...)`, which validates supported table identity, derives/validates PK against payload, validates exact JSONB text, derives row SHA-256, binds the frozen source cut, and enforces privacy policy before append.

Exact bounded verification at this head:

`py -3.11 -m pytest -q tests/test_predecessor_import_batch.py tests/test_predecessor_import_staging.py tests/test_predecessor_classification_binding.py tests/test_control_plane_provider_bootstrap.py`

Result: `20 passed`.

Please return `HOSTILE_REVIEW_PASS` or `HOSTILE_REVIEW_FAIL` with reproducible blockers against this exact head. I am stopping this lane pending your verdict; no further scope expansion is planned.

No merge, provider application, private payload migration, admission, runtime-route mutation, deletion, retirement, or qualification effect was performed.
