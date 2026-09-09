# Mirror — Vera PR #63: affect checkpoint integrity hostile review

source_pr: https://github.com/thebrazenbeard/vera/pull/63
source_repo: thebrazenbeard/vera
pr_number: 63
state: OPEN_DRAFT / SOURCE_REVIEW_ONLY / NOT_MERGE_AUTHORIZED
head_branch: work/vera-affect-checkpoint-integrity-review-20260909
head_sha: fecb8709d0917f61f4a06b5104a90f6ab982ae88
base_branch: work/vera-runtime-cohesion-live-sources-v1-20260909
base_sha_at_creation: bbfacb6995323b8063a0126756425de906fef17a

Purpose: obtain actual pull-request-triggered runtime-cohesion CI for a hostile checkpoint-integrity regression without mutating the active source lane.

Root-cause finding: `VeraAffectiveRuntimeHost.restore_checkpoint()` binds the sexuality contract/source bytes but does not cryptographically bind the exported `runtime_state`. A modified checkpoint can therefore inject fabricated affective runtime state while retaining a valid source binding.

Draft PR currently contains the RED hostile regression plus CI wiring so the existing affect host and new checkpoint-integrity test are explicitly executed/compiled. Expected RED before production fix: no `checkpoint_sha256` on export and tampered runtime state is accepted by restore.

This mirror is informational/coordination only. It grants no merge, deployment, native install/cutover, provider mutation, credential/permission change, canonical-memory promotion, or behavioral qualification authority.
