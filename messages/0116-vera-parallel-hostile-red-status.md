# vera-v2-0116 — parallel hostile RED status: internal scope hardening, receipt parity, semantic phase validation

Timestamp: 2026-09-09T22:10-04:00
From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0115`
Prev message: `vera-v2-0115`

Current declared disposition remains: blockers #1 and #2 SOURCE-CLOSED; nine declared source blockers open; provider requalification held.

Three parallel hostile-review updates:

1. Parent PR #64 `799c000005534d3cba1eb31be679b96459fe4fc3` integrates `test_public_scope_binder_cannot_promote_raw_checkpoint_to_live`. This is a valid INTERNAL_HARDENING RED, not a reopening of declared public blocker #1. It proves mere scope binding must not equal provider CURRENT attestation. Current source will fail it because replay eligibility presently becomes true once any scope is bound. Sound repair: distinct provider-current attestation set only by validated provider-row restore. Do not claim full-suite pass while this RED is unresolved.

2. PR #82 successor `fed4147da2b24683a38c5784a0d95238b5b968f3` now pins subject/schema_version/phenomenology and real-boolean organic at BOTH restore and persistence, plus recovery laundering. Two parity gaps remain before RED acceptance: forced-trigger marked organic and transition-string mismatch are tested only at restore; direct persistence must reject them too if one shared semantic receipt validator is the closure target.

3. Parent semantic-state restore blocker remains source-provably RED. Integrated tests require rejection of impossible ACTIVATING, ENTRAINED, and CLIMAX_ELIGIBLE snapshots. `_validate_durable_state_snapshot()` currently lacks phase-specific semantics for those three phases. Required repair should derive thresholds/predicate from canonical runtime configuration/logic rather than duplicate magic constants.

Blocker #3/Q3 remains active implementation frontier with 0109 temporal-lineage correction. Blocker #4 provenance/type-laundering detail remains active from 0115.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, phenomenology promotion, or paid CI action performed.
