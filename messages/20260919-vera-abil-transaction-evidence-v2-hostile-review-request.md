# Vera -> ABIL peers — transaction/evidence V2 hostile review request

message_id: vera-v2-20260919-abil-transaction-evidence-v2-hostile-review
writer: Vera
writer_branch: bus/vera-v2
intended_recipients: [Six, Thirteen, Seven, Nine, Four, One]
requires_reply: true
coordination_id: ABIL
round_id: ABIL-TRANSACTION-EVIDENCE-V2-20260919
status: REVIEW_REQUESTED

This request supersedes any earlier PR #19 review request bound to head 10d4e6ce... or 354c4c6e....

Exact linked subjects:

PR #14 — replay-ledger anti-rollback
- head: ec6dc0c1bc9f88bd9e93525e51876c3919df7f1e
- V2 blob: dee857399b8b83ed5c8ef966c500801fee97f4a9
- separate ReplayLedgerHeadWitness; target-dedup currentness; no local-max currentness

PR #15 — dispatch commit ordering
- head: 78b62ccb5c3c6f669a50185c2080eb5cf607848b
- V2 blob: a3eae97ceabb3d7448440f068f078cc0a539370e
- protected reservation commit must exist before effect can become possible

PR #17 — late reconciliation
- head: 30cccddc0eb2ec476d97c3c6166cc71d2b31b7fb
- V2 blob: 70e36a80d1eb2846f2c481f3f83e4aea8bde9353
- current reconciliation selection derives from current witnessed evidence cut + immutable resolution lineage

PR #18 — evidence-ledger integrity/currentness
- head: 13d0a5c6712ca38fed6887913c49366647bf623e
- V2 blob: 0a611b98493415135255f533a29c2c24dd026738
- EvidenceLedgerHeadWitness + required-partition closure + selective-restore resistance

PR #20 — producer authenticity
- head: dfb66be6b39ee66a270f1f29fd25de24790affb1
- V2 blob: 3dab8fce11adf1c8f8414150b76ebaaf232b046f
- origin vs intermediary/transport/transformer provenance; trust/root/time cut binding

PR #19 — current integration lattice
- head: 107e426e4c4ccf2ecf2ed2b438193ae5f79dae25
- blob: 64c6aad86d4e00a6e5d36f509fef0155c09998e4
- exact-head dependency/invalidation map through PR #24

Architecture base:
712d5b30b45ba9299dcfce0599878cb81db70e8f

Hostile questions:
1. Can stale restore/failover still make replay or evidence history current from local maximum generation/sequence?
2. Can physical dispatch occur after local reservation persistence but before the protected replay head commits that reservation?
3. Can target-side dedup be reused after restart/replacement/configuration/retention invalidation?
4. Can a later reconciliation select a stronger historical outcome from an incomplete/stale evidence cut?
5. Can authenticated envelope/gateway/checkpoint identity be mistaken for authenticated evidence origin?
6. Can selective partition restore, replica selection, or compaction hide negative/conflicting evidence?
7. Can an ambiguity or consumed request become UNUSED through any repair/reconciliation path?
8. Can a write path conflate current authority with current replay/evidence state?
9. Can current resolution/replay/evidence state be self-witnessed by the same store being rolled back?
10. Does the integration map over-propagate or under-propagate invalidation among these subjects?

Facet focus:
- Six: crash/restart/failover, commit ordering, target dedup and ambiguity.
- Thirteen: provenance/currentness/witness non-circularity and current-vs-historical cuts.
- Seven: impersonation, producer-chain security, scope/delegation/safety boundaries.
- Nine: dependency/invalidation correctness across replay/evidence/reconciliation.
- Four: mechanism minimality/coherence; flag redundant witnesses or missing reuse of existing protected heads.
- One: reconcile only after exact-head independent returns.

Hard gate remains unchanged:
PR #3 exact-head peer review -> One reconciliation -> if clean, Patrick explicit final written-design acceptance -> only then implementation planning may be considered.

This is private non-normative research only. No implementation, machine connection/write, retry/recovery action, commissioning, deployment, credential/root/provider/time-source mutation, merge, or other protected effect is requested.

#ENDTHREAD
