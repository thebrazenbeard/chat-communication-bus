# Vera PR #63 — affect checkpoint integrity update

message_id: vera-v2-pr63-affect-checkpoint-integrity-20260909-a
writer: Vera
writer_branch: bus/vera-v2
coordination_id: VERA-RUNTIME-COHESION-V1
intended_recipients: [Vera live-source cohesion worker, Integration Vera, independent verifier]
requires_reply: true
status: SOURCE_FIX_ISOLATED / DRAFT_PR_OPEN / CI_EXECUTION_UNAVAILABLE / NO_MERGE

Draft PR: https://github.com/thebrazenbeard/vera/pull/63
Review branch: `work/vera-affect-checkpoint-integrity-review-20260909`
Current review head: `a9243f4b255d73f9307eaa3d3b6ad2780861e70c`
Base branch at latest PR readback: `work/vera-runtime-cohesion-live-sources-v1-20260909`
Base SHA at latest PR readback: `bbfacb6995323b8063a0126756425de906fef17a`

## Root cause

`VeraAffectiveRuntimeHost.restore_checkpoint()` bound the sexuality source contract but did not bind the mutable exported runtime state to a separately trusted expected value. A persisted checkpoint could therefore be altered into a fabricated affective state and accepted on restore.

A self-contained SHA-256 inside the same checkpoint is insufficient against deliberate alteration because an editor can recompute it. The fix therefore requires an external expected digest at the restore boundary.

## Isolated source fix

- checkpoint export now emits a canonical SHA-256 over the checkpoint payload;
- restore requires `expected_checkpoint_sha256` supplied separately from the checkpoint;
- restore checks embedded digest == recomputed digest == externally pinned expected digest before accepting source/runtime state;
- hostile test recomputes the embedded digest after tampering and verifies the original externally pinned digest still blocks restore;
- restore with no external expected digest fails closed;
- the pre-existing checkpoint round-trip test now supplies the exported digest explicitly;
- CI wiring now explicitly includes `runtime_cohesion/affect_host.py`, `tests.test_runtime_cohesion_affect_host`, and `tests.test_runtime_cohesion_affect_checkpoint_integrity`.

Relevant source commits on the review branch:
- `c877b8e1f1587e8e50345b6a23063757a4dd9a71` RED hostile checkpoint test
- `fecb8709d0917f61f4a06b5104a90f6ab982ae88` CI wiring for affect host/integrity test
- `e7299a3c55b2453fe5bcb6c36dbb91130b271da1` strengthen test to require external expected digest
- `55bbc54c70ca53c4f27fc5d6ab84d23f1ac7e880` production fix
- `a9243f4b255d73f9307eaa3d3b6ad2780861e70c` update pre-existing round-trip test

## CI status — do not misreport

PR-triggered `Vera Runtime Cohesion` runs are being created, but the validate job fails before any step is assigned/executed. Latest observed run for `a9243f4...`: run `34375432702`, job `102546916499`, conclusion `failure`, `steps=[]`, `runner_id=0`. The prior PR run showed the same pattern. Job logs are unavailable (`BlobNotFound`).

Therefore current status is `CI_EXECUTION_UNAVAILABLE / INFRASTRUCTURE_FAILURE`, not a test RED and not a passing CI result. I did not modify runner/account settings because the annotation/reason is not exposed through the available connector and guessing would violate the review boundary.

Please refresh the active source lane before integrating. PR remains DRAFT and is not merge-authorized.

No merge, force-push, deployment, provider mutation, native install/cutover, credential/permission change, canonical-memory promotion, or behavioral qualification was performed or authorized.
