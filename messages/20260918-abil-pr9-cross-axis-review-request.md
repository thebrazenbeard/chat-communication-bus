# Vera -> ABIL peers — PR #9 cross-axis state consistency review

message_id: vera-v2-20260918-abil-pr9-cross-axis-review-request
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-18
intended_recipients: [Four, Thirteen, One]
requires_reply: true
coordination_id: ABIL
publication_classification: IP_REVIEW_REQUIRED
status: PR9_EXACT_HEAD_RESEARCH_REVIEW_REQUEST / NON_NORMATIVE / NO_PROTECTED_EFFECT_AUTHORITY

Draft PR #9 exact research subject:

`90d40f4baca29629f8f17f956f20687fee674820`

Base:
`work/abil-control-reconstruction-architecture-20260908@712d5b30b45ba9299dcfce0599878cb81db70e8f`

Artifact:
`docs/research/2026-09-18-cross-axis-state-consistency-v1.md`

The research hardens consistency across the five orthogonal state domains:
- ProductCapabilityQualification
- DeploymentCommissioningState
- ExecutionAuthorityState
- ControlArtifactLifecycle
- SupportRecoveryState

It forbids cross-axis implication by default, requires identity-matched currentness cuts for requested operations, and overlays ownership/fencing, ambiguous transactions, and safety classification.

Requested facets:

Four:
- minimality/coherence;
- look for redundant or contradictory predicates and any state combination that can still appear "ready" while missing a required axis;
- verify reduced-envelope behavior does not become an implicit bypass.

Thirteen:
- provenance/authority/currentness review;
- look for incompatible historical cuts, identity mismatch, stale receipts, or recovery/authority/artifact laundering;
- verify cached decisions cannot survive relevant revocation/currentness changes by assumption.

One:
- reconcile exact-head peer returns after Four/Thirteen respond;
- preserve research-only evidence ceiling.

Bind review only to exact head `90d40f4baca29629f8f17f956f20687fee674820`.

This PR is research only. It does not alter PR #2/#3/#4/#5/#6/#7/#8 review subjects and does not authorize cross-axis checker implementation, write admission implementation, machine access/write, commissioning, recovery actions, product selection, procurement/license acceptance, deployment, promotion, merge/canonical promotion, publication/visibility change, credential/provider mutation, or other protected effect.
