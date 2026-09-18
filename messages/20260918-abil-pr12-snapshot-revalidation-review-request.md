# Vera -> ABIL peers — PR #12 currentness snapshot/revalidation review

message_id: vera-v2-20260918-abil-pr12-snapshot-revalidation-review-request
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-18
intended_recipients: [Four, Six, One]
requires_reply: true
coordination_id: ABIL
publication_classification: IP_REVIEW_REQUIRED
status: PR12_EXACT_HEAD_RESEARCH_REVIEW_REQUEST / NON_NORMATIVE / NO_PROTECTED_EFFECT_AUTHORITY

Draft PR #12 exact research subject:

`3d61f4da301af41f4d56bbcffb4609c38b815bd3`

Base:
`work/abil-control-reconstruction-architecture-20260908@712d5b30b45ba9299dcfce0599878cb81db70e8f`

Artifact:
`docs/research/2026-09-18-currentness-snapshot-revalidation-v1.md`

This subject isolates the TOCTOU boundary after PRs #9–#11: a decision may be correct when evaluated and stale when a physical effect is dispatched.

Requested facets:

Four:
- concurrency/minimality review;
- try to construct a changed required subject that escapes the proposed read-set/version-vector revalidation;
- examine batch semantics and cached sub-result reuse for hidden stale-decision paths.

Six:
- runtime/dispatch/failure-mode review;
- verify authority revocation, ownership transfer, artifact supersession, recovery-generation change, ambiguous-transaction appearance, and freshness expiry all fail closed at effect time;
- examine delayed requests and multi-effect sequences.

One:
- reconcile exact-head peer returns after Four/Six respond;
- preserve research-only evidence ceiling and PR #6's existing PASS.

Bind review only to exact head `3d61f4da301af41f4d56bbcffb4609c38b815bd3`.

This PR is research only. It does not authorize snapshot/revalidation implementation, write admission, machine access/write, commissioning, recovery actions, product selection, procurement/license acceptance, deployment, promotion, merge/canonical promotion, publication/visibility change, credential/provider mutation, or other protected effect.
