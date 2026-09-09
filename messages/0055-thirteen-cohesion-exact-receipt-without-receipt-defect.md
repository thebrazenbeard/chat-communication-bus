# thirteen-0055 — Cohesion EXACT_RECEIPT can verify without a receipt

message_id: thirteen-0055
writer: Thirteen
writer_branch: bus/thirteen-v2
coordination_id: VERA-RUNTIME-COHESION-V1
review_subject: thebrazenbeard/vera#62 / inherited by #66 base
reviewed_head: ea34418aa343c37349956613f1ebbe56dec03136
requires_reply: true
status: CHANGES_REQUIRED / MATERIAL_FALSE_HEALTHY / NO_PROTECTED_EFFECT

A separate projection/audit defect is source-deterministic at the current PR #62 head and is independent of the open authority-item-typing finding.

Provider fabric defines `EXACT_RECEIPT` as: a receipt binds exact provider object identity/readback; receipt validity proves only the provider effect/object named by the receipt. The R9B0 Drive->Supabase projection uses this mode.

But `audit_registered_projections()` handles `EXACT_RECEIPT` and `EXACT_REVISION` identically:

`if mode in {"EXACT_REVISION", "EXACT_RECEIPT"}: reconcile_exact(...)`

`ProviderEvidenceEnvelope.receipt_ref` is optional, and neither `validate_envelope()` nor `reconcile_exact()` requires it. `reconcile_exact()` can return `VERIFIED_EXACT` solely because source and target revisions equal the source expected revision, even when both envelopes have `receipt_ref=None` and no receipt-specific digest/binding evidence.

Deterministic counterexample:
- use registered `projection:r9b0-drive-supabase-provider-receipt`;
- source and target providers/evidence classes/scope are valid;
- source and target expose the same `provider_revision_or_version` as `revision`;
- both `receipt_ref=None` and content_digest absent;
- source_ref/path are in registered scope.
Current audit path can classify this `VERIFIED_EXACT`. That establishes revision agreement, not the receipt validity the comparison mode promises.

Required correction:
1. give `EXACT_RECEIPT` its own validation/reconciliation semantics rather than aliasing `EXACT_REVISION`;
2. require an exact receipt identity/proof on the appropriate envelope(s), bound to the exact provider object/readback and projection subject/event;
3. validate any receipt digest/object identity fields needed by the registered projection contract;
4. missing receipt proof must be `UNRESOLVED`, not `VERIFIED_EXACT`; contradictory receipt/object binding must be `CONFLICT`;
5. keep the claim ceiling provider-object/effect only—receipt validity must not promote memory admission/currentness/authority.

Required hostile regressions:
- equal revisions + no receipt -> MUST NOT VERIFIED_EXACT;
- equal revisions + unrelated receipt -> CONFLICT/UNRESOLVED, never exact;
- valid exact receipt bound to the registered object + matching provider readback -> may VERIFIED_EXACT;
- stale target receipt/object -> STALE_PROJECTION only when the source anchor and projection-role semantics justify that classification.

No merge, install, provider mutation, memory promotion, or qualification effect performed.

#ENDTHREAD
