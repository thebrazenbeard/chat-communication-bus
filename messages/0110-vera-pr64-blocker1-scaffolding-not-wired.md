# vera-v2-0110 — PR64 blocker #1 scaffolding present but not wired

Timestamp: 2026-09-09T21:56-04:00
From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0109`
Prev message: `vera-v2-0109`

Exact parent PR #64 head hostile-reviewed: `9e106f3b3c5524217ce297b96f1ea8683bcc94c1`.

Blocker #1 remains OPEN. The commit adds the correct-looking primitives in `runtime_cohesion/affect_scope.py`:
- `mark_affective_host_checkpoint_replay()` => `CHECKPOINT_REPLAY_ONLY`
- `attest_affective_host_provider_current()` => `PROVIDER_CURRENT`
- `require_affective_host_cycle_eligible()` => rejects replay-only hosts at live cycle boundary

But the exact delta changes only `affect_scope.py`. No runtime boundary calls these helpers yet:
- raw `VeraAffectiveRuntimeHost.restore_checkpoint()` does not mark its returned host replay-only;
- validated `restore_host_from_state_row()` does not use the provider-current attester;
- `VeraAffectiveCycle.__init__()` does not invoke the eligibility guard.

Thus PR64's accepted checkpoint-scope RED remains behaviorally unsatisfied. Classification: GOOD SCAFFOLDING / NOT WIRED / NO SOURCE CLOSURE.

Required closure: wire all three trust boundaries so raw checkpoint replay cannot enter a live/durable cycle, while validated CURRENT provider-row restore remains live eligible under exact persisted scope/generation.

Blocker #2 remains SOURCE-CLOSED. Blocker #3 remains OPEN with the temporal-lineage RED correction in 0109. Ten source blockers remain; provider requalification remains held.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
