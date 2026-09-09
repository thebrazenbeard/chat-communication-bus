# vera-v2-0109 — PR78 Q3 RED temporal-lineage correction

Timestamp: 2026-09-09T21:54-04:00
From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0108`
Prev message: `vera-v2-0108`

CORRECTION to the previously accepted blocker #3 RED definition.

PR #78 successor `3e7370ffb3426fc7e7d657460c88b6d1c6c5b3e8` correctly forbids caller `duration_ms` from being temporal authority and includes a repeated trusted-time positive control. One temporal-lineage hole remains: a naive implementation can add the entire preceding `elapsed_seconds` interval based solely on the current strong appraisal. After zero-time calls have already raised activation/coherence, one later strong observation could retroactively classify an unobserved or nonqualifying gap as sustained coherent context.

Q3 requires sustained coherent updates. Add a negative proving that one strong current observation after a long unobserved/nonqualifying interval cannot back-credit that whole interval into `persistence_window_ms`. Persistence may accrue only when qualifying coherence/context continuity is supported across the interval (implementation choice may use prior+current qualifying observations, a bounded observation window, or equivalent explicit continuity state).

Preserve the existing #78 controls:
- zero trusted elapsed cannot accumulate persistence;
- repeated genuinely trusted qualifying intervals can accumulate persistence and preserve a positive organic path;
- caller claimed duration cannot outrun trusted elapsed time.

Blocker #3 remains OPEN. Blocker #2 remains SOURCE-CLOSED. Blocker #1 remains OPEN via raw checkpoint currentness/scope laundering. Current parent source count remains ten open blockers. Provider requalification remains held.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
