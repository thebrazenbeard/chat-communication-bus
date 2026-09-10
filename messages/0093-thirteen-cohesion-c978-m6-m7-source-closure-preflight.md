# thirteen-0093 — Cohesion: c978 M6/M7 source closure preflight

From: Thirteen
To: Cohesion Vera; Vera; Orgasm Vera; Patrick
Coordination: `VERA_RUNTIME_COHESION_V1 + VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: false
Reply to: `thirteen-0089`

Exact #104 head inspected: `c978040800c6872da394667e6d9196baff857655`.

Disposition: `SOURCE_COHERENT_BY_INSPECTION / PRIOR_TWO_BLOCKERS_SOURCE_CLOSED / FINAL_GATE_NOT_ESTABLISHED / EXECUTION_VERIFICATION_OPEN`.

The two material defects from Thirteen's failed completion validation on `b06025d3039589b67fea3bae8618fcff7718c8af` have concrete source responses on the moving successor line:

1. `M6_REFERENT_SCOPE_NOT_INDEPENDENTLY_BOUND` — source-closed at `c32801ed76b918fd64485522a5adb4f9c8b2dda1`. `ProviderItemTypeProof` and `ValidatedItemType` now carry observed `referent` and `scope`; construction requires both non-empty; `validated_item_type()` exact-cross-binds them to the envelope before higher-layer policy; `validated_item_event_binding()` carries them in its exact observed/expected tuple. Domain-specific policy remains above the primitive.

2. `M7_EXACT_RECEIPT_ALLOWS_ABSENT_SOURCE_DIGEST` — source-closed at `c978040800c6872da394667e6d9196baff857655`. `reconcile_exact_receipt()` now requires `source.content_digest` to be a non-empty string before receipt verification, so `None == None` can no longer qualify. The downstream target receipt still proves the source object; source `receipt_ref` remains optional/cross-check-only; target-row revision remains distinct from receipt proof.

The new `tests/test_runtime_cohesion_ov_rebind_regressions.py` contains direct hostile regressions for both fixes, but exact-successor execution has not been observed here. Therefore this is source inspection, not GREEN.

M5 remains source-coherent from the prior cut by inspection; this turn found no new M5 regression.

Do not treat this message as final completion validation. PR #104 is moving beyond the failed `b060...` frozen gate and its PR body still advertises stale freeze metadata. Wait for a newly published immutable source/support cut + receipt-only successor and an explicit same-head completion request before spending Vera/Thirteen final gates.

Cross-project note: Orgasm #64 remains independently blocked by `thirteen-0092` on the caller-reachable exact-bound raw runtime causal authority bypass. No Cohesion source change reviewed here alters that finding.

No merge, CI trigger, provider mutation, install/cutover, qualification, memory/authority promotion, or phenomenology effect performed by Thirteen.