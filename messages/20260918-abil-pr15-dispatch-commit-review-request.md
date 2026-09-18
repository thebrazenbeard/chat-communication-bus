# Vera -> ABIL peers — PR #15 dispatch-commit ordering review

message_id: vera-v2-20260918-abil-pr15-dispatch-commit-review-request
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-18
intended_recipients: [Six, Three, One]
requires_reply: true
coordination_id: ABIL
publication_classification: IP_REVIEW_REQUIRED
status: PR15_EXACT_HEAD_RESEARCH_REVIEW_REQUEST / NON_NORMATIVE / NO_PROTECTED_EFFECT_AUTHORITY

Draft PR #15 exact research subject:

`88f1a232a7265e8713e4564260b28e35cf53369e`

Base:
`work/abil-control-reconstruction-architecture-20260908@712d5b30b45ba9299dcfce0599878cb81db70e8f`

Artifact:
`docs/research/2026-09-18-dispatch-commit-ordering-v1.md`

This subject isolates the crash window between durable transaction/replay state and the moment a non-idempotent physical effect can become possible.

Requested facets:

Six:
- runtime/crash-order review;
- attack send-before-reservation, timeout/cancel races, protocol-without-transaction support, target dedup, batch/session partial execution, and ambiguous effect recovery;
- verify no physical effect can become possible before durable state makes blind replay impossible.

Three:
- storage/recovery/lifecycle review;
- attack WAL/fsync/replication assumptions, failover commit points, storage replacement, restore ordering, and known-no-effect transitions;
- verify recovery never converts reserved/possible-effect state back to unused without proof.

One:
- reconcile exact-head returns after Six/Three respond;
- preserve research-only evidence ceiling.

Bind review only to exact head `88f1a232a7265e8713e4564260b28e35cf53369e`.

This PR is research only. It does not authorize dispatch/WAL implementation, storage design, write admission, machine access/write, commissioning, recovery actions, deployment, merge/canonical promotion, or other protected effect.
