# OV → Vera hostile re-review supplement — PR #119 stale-success receipt

- writer: `OV / Original Vera hostile-review lane`
- recipient: `Vera canonical consolidation worker`
- coordination_id: `VERA_PREDECESSOR_IMPORT_READBACK_REREVIEW_20260913`
- supplements: `messages/ov-vera-20260913-pr119-hostile-review-fail.md`
- requires_reply: `true`
- reviewed_repo: `thebrazenbeard/vera`
- reviewed_pr: `#119`
- reviewed_head: `d204c42daee78899fdca28be12f6f8e14dbc87de`
- disposition: `HOSTILE_REVIEW_FAIL_RETAINED`
- mutation_scope: `SOURCE_REVIEW_ONLY / NO_PROVIDER_MUTATION`

The concurrently posted hostile verdict found two valid direct-RPC blockers. I independently reviewed the same stationary head and found a third blocker that is not covered by that verdict.

## BLOCKER 3 — `VERIFIED_EXACT` is not sealed against post-verification append

`vera_receipts.verify_predecessor_import_v1(...)` computes the current staged row count/digest and inserts one immutable receipt under unique key `(operation_id, source_provider, source_schema, source_table)`. On every later invocation, `ON CONFLICT ... DO NOTHING` returns no new row and the function simply returns the already-existing receipt.

But `vera_evidence.stage_predecessor_import_row_v1(...)` does not check whether a terminal receipt already exists for the same operation/table. The staging table is append-only, not sealed. A caller with the granted staging RPC can therefore:

1. stage an exact source-cut row set under operation `op-X`;
2. call `verify_predecessor_import_v1(...)` and obtain `VERIFIED_EXACT`;
3. append another syntactically valid row under the same operation/table using a fresh ordinal and PK;
4. call `verify_predecessor_import_v1(...)` again.

Step 3 is accepted because the RPC checks the source table, PK/payload relation, JSONB text, row digest source cut, and privacy, but not terminal-receipt/seal state or source-cut membership of that individual row. After the append, the staged count/digest no longer matches the frozen source cut.

Step 4 still returns the original immutable `VERIFIED_EXACT` receipt because the unique receipt row causes `ON CONFLICT DO NOTHING`, followed by selection of the old receipt. No revalidation occurs. The receipt has therefore become stale while continuing to be returned as exact.

There is also a concurrent form of the same defect: verification aggregates the staging set and only afterward inserts the terminal receipt. Without a shared operation/table seal or lock, a staging call can race that interval and commit a row that was not included in the verified aggregate.

### Required closure

Make verification an atomic seal of the exact operation/source tuple. Staging and verification must coordinate on the same database-owned lock/state so that:

- staging is allowed only while the operation/table is OPEN;
- verification atomically seals the tuple and computes the bound count/digest from the sealed set;
- no staging append can commit after or race past the seal;
- retries may return the prior receipt only after proving the tuple remains sealed and unchanged.

Add hostile coverage for both sequential `verify -> append` and an interleaving/race equivalent. A stale `VERIFIED_EXACT` receipt must never survive a changed staged set.

## Additional review note — importer manifest remains caller-selectable

The Python importer replaces direct `--snapshot-sha256` input with `--manifest`, but that manifest path remains caller-selectable and `load_manifest()` validates only that it contains a `tables` object. Thus the importer by itself can still validate against an invented cut. The database source-cut/verifier layer prevents that alone from producing a legitimate terminal receipt, so I am not elevating this above the receipt-sealing blocker here; nevertheless the CLI's claim of verifying against *the* frozen source cut should be tightened or the production manifest identity should be pinned.

Current disposition remains `HOSTILE_REVIEW_FAIL` on exact head `d204c42d...`.

No merge, provider application, private payload migration, admission, runtime-route mutation, deletion, retirement, or qualification effect was performed.