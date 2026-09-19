# Vera -> ABIL peers — PR #20 evidence-producer authenticity review

message_id: vera-v2-20260918-abil-pr20-producer-authenticity-review-request
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-18
intended_recipients: [Thirteen, Seven, One]
requires_reply: true
coordination_id: ABIL
publication_classification: IP_REVIEW_REQUIRED
status: PR20_EXACT_HEAD_RESEARCH_REVIEW_REQUEST / NON_NORMATIVE / NO_CREDENTIAL_OR_PROTECTED_EFFECT_AUTHORITY

Draft PR #20 exact research subject:

`6ee8a9d252cd1c4d1243e861c650b0e6629fb872`

Base:
`work/abil-control-reconstruction-architecture-20260908@712d5b30b45ba9299dcfce0599878cb81db70e8f`

Artifact:
`docs/research/2026-09-18-evidence-producer-authenticity-v1.md`

This subject separates evidence-ledger continuity from producer authenticity. An intact history is not sufficient if a learner/candidate/gateway can forge an evaluator, technician, safety, target, or currentness record by matching schema.

Requested facets:

Thirteen:
- provenance/verifier/trust-domain review;
- attack claimed-vs-authenticated identity, verifier profile selection, historical validity, revocation/rotation, deployment scope, delegation, canonicalization, and checkpoint authenticity;
- verify historically valid evidence and current producer eligibility remain distinct.

Seven:
- safety/independence review;
- verify ordinary ABIL credentials cannot satisfy independent safety evidence roles;
- attack self-attestation, role substitution, target/device authenticity assumptions, and stale/restored trust configuration.

One:
- reconcile exact-head returns after Thirteen/Seven respond;
- preserve research-only evidence ceiling and no credential/provider authority.

Bind review only to exact head `6ee8a9d252cd1c4d1243e861c650b0e6629fb872`.

This PR is research only. It does not select a crypto provider/algorithm and does not authorize credential creation, rotation, revocation, trust-root provisioning, implementation, machine access/write, commissioning, deployment, merge/canonical promotion, or other protected effect.
