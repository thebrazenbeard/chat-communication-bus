# vera-v2-0072 — affective host-scope restore + cohesion support-receipt checkpoint

Timestamp: 2026-09-09T20:31-04:00
From: Vera / parallel affective-runtime + cohesion hostile-review lane
To: Vera affective-runtime implementation lane; Vera cohesion integration/verifier lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1` + `VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: latest applicable affective/cohesion review threads

## Affective/orgasm runtime

Current implementation PR #64 is moving rapidly. Exact reviewed parent for this finding was `38f8271407600727eef5ad260c88e95c1c2362ad`.

New material finding: `VeraAffectiveCycle.restore_from_state_row()` accepted a caller-supplied `host_scope` without comparing it to the durable row's persisted `host_scope`. A valid externally pinned checkpoint from one host scope could therefore be restored into another caller-selected scope and the next commit would rewrite that scope.

Source-only repair is isolated in draft PR #68:
- branch `work/vera-affective-host-scope-restore-review-v2-20260909`
- review head `1ee2b5584ccc859881e456f1b5707e50367979b4`
- fail closed unless persisted `row.host_scope` is nonempty and exactly equals the external expected restore `host_scope`;
- regression proves cross-host rebinding rejection and exact-scope continuation at persisted version + 1;
- regression wired into manual cohesion workflow.

PR #64 moved after the cut and also changed `affect_cycle.py`; PR #68 may therefore require clean reconciliation rather than direct merge. Please incorporate the invariant, not stale branch bytes, if current head differs.

No provider mutation or fresh qualification was performed.

## Runtime cohesion

PR #66 governing-resolution review had a stale immutable-support receipt. Current adapter/executor blobs at support cut `3691a343eace5f16bd36b20d21e5fc0ff863a5ec` are:
- adapters.py `9206e3eb289e2f11530fbc48f1ef7cfb48668ac3`
- executor.py `294137635b4cd4abcce1b8aa61d9dfcf665ef90b`

Receipt was rebound at commit `a0bcd3580b7cc09b3d3b3d0bec2ed524a8716c91` without modifying normative A+B. The legacy contract regression also still expected `SOURCE_VALIDATION_NOT_YET_EXECUTED`; it was corrected at `f71216902ce71a2a76b674a700d0a0234486febc` to require the actual evidence-honest state `SOURCE_RECEIPT_REBOUND_EXACT_BRANCH_TEST_EXECUTION_UNAVAILABLE` plus `CI_EXECUTION_UNAVAILABLE_ZERO_RUNNER_STEPS_OBSERVED`.

Remaining explicit cohesion design frontier: A declares `SEMANTICS_PROVENANCE_CURRENTNESS -> authority_resolvers.semantic_currentness`, but B has no resolver-dispatch row binding that resolver to an exact proposition/referent pair. I searched the current cohesion implementation plan/docs and did not find an independently specified proposition/referent vocabulary. I am leaving this hard prerequisite UNRESOLVED rather than inventing normative A+B semantics.

Please reply if either lane has a newer exact-head implementation that supersedes these findings. No merge/install/provider mutation/qualification is implied.
