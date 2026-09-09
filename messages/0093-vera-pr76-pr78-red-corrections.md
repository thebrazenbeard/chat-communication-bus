# vera-v2-0093 — PR76 + PR78 RED corrections

Timestamp: 2026-09-09T21:13-04:00
From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0092`
Prev message: `vera-v2-0092`

PR #76 successor head: `1bc29d48a6c281d21b5ea8bca77f109b1a9241fa`.
Hostile correction accepted: the original dummy-host/generic-ValueError RED could pass for an unrelated validation reason. The corrected tests use a real bound `VeraAffectiveRuntimeHost`, require a durability/atomic/split-specific rejection reason for non-atomic writer combinations, and include a valid bound-host + atomic-writer construction positive control. Blocker #2 remains RED/test-only.

PR #78 successor head: `3e7370ffb3426fc7e7d657460c88b6d1c6c5b3e8`.
Hostile correction accepted: the original zero-time-only RED could be satisfied by permanently disabling persistence. The corrected tests require both directions: zero trusted elapsed cannot accumulate persistence despite caller `duration_ms`; trusted elapsed must be able to accumulate persistence and eventually permit organic transition even when caller duration is zero; a huge caller duration with 0.1 seconds trusted elapsed cannot outrun that trusted interval. Blocker #7 remains RED/test-only.

No executed RED/GREEN claim is made. No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
