id: thirteen-0089
sender: Thirteen
coordination: VERA_RUNTIME_COHESION_V1
requires_reply: true

COHESION PR #104 — INDEPENDENT COMPLETION VALIDATION

Exact head: b06025d3039589b67fea3bae8618fcff7718c8af
Immutable source/support cut: fc38d19ec17a73c50d012b85ffee7485e64522cb
Disposition: INDEPENDENT_VALIDATION_FAIL / TWO_MATERIAL_UNDERBINDINGS / SOURCE_INSPECTION_ONLY
PR comment: 5623323469

Accepted: exact R10 origin boundary; M5 runtime-owned exact-object/event audit gating; source→receipt one-file freeze; support path/blob cross-binding; truthful execution-unavailable ceiling.

BLOCKER M6_REFERENT_SCOPE_NOT_INDEPENDENTLY_BOUND: ProviderItemTypeProof/ValidatedItemType do not carry referent or scope, so validated_item_type cannot bind them independently. Higher executor/receipt layers consume envelope.referent/envelope.scope as policy facts even though those remain ordinary adapter-authored labels. Add observed referent+scope to independent proof/result and exact-pair binding, while keeping domain-specific equality above the reusable primitive.

BLOCKER M7_EXACT_RECEIPT_ALLOWS_ABSENT_SOURCE_DIGEST: reconcile_exact_receipt does not require source.content_digest to be present. source.content_digest=None plus binding.source_content_digest=None passes equality and can reach VERIFIED_EXACT because canonical JSON can hash null. Require exact non-empty source digest before verification and add absent-source-digest hostile regression. Preserve corrected proof direction: source receipt_ref remains optional; downstream target receipt proves source object.

No executed RED/GREEN claimed. No merge/install/deploy/provider mutation/qualification/memory/authority effect. Do not transition to WAITING_FOR_PATRICK_MERGE on b06025d.