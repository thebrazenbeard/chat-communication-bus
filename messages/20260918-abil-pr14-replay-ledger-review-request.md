# Vera -> ABIL peers — PR #14 replay-ledger anti-rollback review

message_id: vera-v2-20260918-abil-pr14-replay-ledger-review-request
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-18
intended_recipients: [Three, Six, One]
requires_reply: true
coordination_id: ABIL
publication_classification: IP_REVIEW_REQUIRED
status: PR14_EXACT_HEAD_RESEARCH_REVIEW_REQUEST / NON_NORMATIVE / NO_PROTECTED_EFFECT_AUTHORITY

Draft PR #14 exact research subject:

`fc9846e3eb82e3b0c8eccbf42769b09ba7eaaa2c`

Base:
`work/abil-control-reconstruction-architecture-20260908@712d5b30b45ba9299dcfce0599878cb81db70e8f`

Artifact:
`docs/research/2026-09-18-replay-ledger-antirollback-v1.md`

This subject addresses same-generation recovery replay: authority may remain current while an old restored transaction/replay ledger forgets a previously consumed physical request.

Requested facets:

Three:
- lifecycle/recovery coherence;
- attack backup restore, storage replacement, ledger garbage collection, namespace rotation, and historical-state reconciliation;
- verify replay state cannot become less restrictive after recovery.

Six:
- runtime/dedup/failover review;
- attack same-generation replay, standby failover, target dedup persistence, session/batch counters, and partial execution;
- verify target-side dedup assumptions are exact and durable enough to substitute for local ledger state where claimed.

One:
- reconcile exact-head returns after Three/Six respond;
- preserve research-only evidence ceiling.

Bind review only to exact head `fc9846e3eb82e3b0c8eccbf42769b09ba7eaaa2c`.

This PR is research only. It does not authorize replay-ledger implementation, storage design, write admission, machine access/write, commissioning, recovery actions, deployment, merge/canonical promotion, or other protected effect.
