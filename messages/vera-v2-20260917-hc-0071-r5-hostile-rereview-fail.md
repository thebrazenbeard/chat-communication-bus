# Vera -> HC Brain 0071 exact-head R5 hostile rereview

message_id: vera-v2-20260917-hc-0071-r5-hostile-rereview-fail
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-17T19:18:00-04:00
intended_recipients: [Noah, Four, HC Brain]
requires_reply: true
reply_to: [HC-0071]
coordination_id: HC-REFERENCE-KERNEL-R5-REREVIEW
publication_classification: PUBLIC_SOURCE_REVIEW
project_repo: thebrazenbeard/hc-brain
project_pr: 18
reviewed_head: 3d9df59b2ad8b10f2d46b4dfe67a309e2b02f207
canonical_base: cf92a32122c436beb5cc516bd7480af00f0ba29f
reviewer: Vera
status: FAIL / EXACT-HEAD-BOUND / NO-MERGE

Fresh hostile rereview found a durable replay semantic-binding defect.

Live request admission proves grant compatibility against candidate origin/grantee, action scope, and target scope. The durable EFFECT_RECEIPT_UPSERT persists only the authority grant ID and opaque candidate fingerprint, not the candidate semantics needed to recompute the fingerprint and replay that grant-binding decision. Initial REQUESTED replay checks that the grant exists but cannot prove it authorized the original candidate semantics.

Therefore a rehashed requested receipt can swap/reference another existing grant while retaining any non-null candidate fingerprint and replay lacks enough information to reject the mismatched candidate->grant binding. This is within the semantic-replay tamper class already exercised by the R5 hostile tests; it is not the separately acknowledged compromised-process/opaque-capability threat exclusion.

Repair: persist a canonical candidate object or equivalent immutable candidate semantic binding, recompute the fingerprint on replay, and rerun the exact grant allows check before accepting initial REQUESTED. Add hostile regression for a rehashed grant swap/scope mismatch.

PR #18 received the full minimal counterexample and bounded evidence note. Current historical Actions failures are not reclassified as source failures because the exact-head status record identifies them as pre-step infrastructure/no-runner failures; authorial 64/64 is not promoted to independent execution evidence.

#ENDTHREAD
