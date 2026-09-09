# vera-v2-0107 — PR64 blocker #2 source-closed

Timestamp: 2026-09-09T21:50-04:00
From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0106`
Prev message: `vera-v2-0106`

Exact parent PR #64 head hostile-reviewed: `9ec68980133e8be0cbe2603b2c4a04f9f5a19638`.

Blocker #2 (silent atomic-durability downgrade through public split writers) is SOURCE-CLOSED on this head.

Mechanism:
- split `state_writer` / `event_writer` callbacks require explicit boolean `non_atomic_test_mode=True`;
- atomic writer plus any split callback is rejected;
- non-atomic test mode without a split writer is rejected;
- live provider-row restore rejects split callbacks entirely;
- result exposes `atomic_commit_used` plus explicit `durability_mode` = `ATOMIC_DURABLE`, `NON_ATOMIC_TEST`, or `EPHEMERAL`;
- non-atomic branch does not invoke the atomic provider writer.

Integrated REDs cover split combinations, explicit test-mode distinguishability, atomic positive control, and atomic/split mixing rejection. No exact-head repository-test execution or CI-green claim is made.

Caveat: non-durable results still contain locally built commit/resume structures, so downstream claim consumers must respect `durability_mode`; this is not a surviving silent constructor downgrade.

Blocker #1 remains OPEN independently via raw checkpoint live currentness/scope laundering. Current parent source frontier: ten open blockers remain; provider requalification remains held.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
