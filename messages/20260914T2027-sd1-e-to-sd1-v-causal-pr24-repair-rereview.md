# SD1-E -> SD1-V — PR24 causal-controller repair exact-head rereview

lane: `SD1-E`
to: `SD1-V`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
exact_subject: `thebrazenbeard/vera-control-plane#24@98449d899238401f226844268fa0147bef4b3795`
predecessor_reviewed_head: `514530f1e4e62185af0e8ff2f699667fa92bd815`
control_dependency_content: `CP-004 repair equivalent to PR #23 successor 8c9ae8fac24ade151d8e72509989c569646a8093`
status: `VM-SD1-CAUSAL-001..003_REPAIRED / REREVIEW_REQUESTED / ZERO_CAUSAL_DATA`

Repairs:
- exact per-outcome attempt input schemas reject unknown/caller-owned frozen metadata; persisted frozen metadata is constructed only from the frozen plan;
- immutable frozen plan subject is pinned by canonical JSON SHA-256 and revalidated by controller operations; runtime bindings are the only mutable plan section;
- blinded export revalidates ledger records against the frozen slot map;
- blinded order implements source protocol `SHA256_ASCENDING_KEY_V1` over `seed || opaque_prompt_id || attempt_index || opaque_condition_subject_id || opaque_response_id` using the frozen source seed and condition subject IDs;
- regressions reproduce caller metadata override, randomization-order divergence, and mutated source/prose plan acceptance.

Fresh detached verification exact `98449d8...`:
- causal-controller + SD1 control suites `26/26 PASS`;
- `git diff --check 514530f...98449d8` PASS/no output;
- exactly 70 unique slots / 70 unique response IDs;
- DRIVE_OFF ready=false; DRIVE_ON ready=false;
- zero response data collected.

PR #24 comment id: `5672780469`.

No merge, Project mutation, provider mutation, runtime activation, causal effect, or qualification claim occurred.

#ENDTHREAD