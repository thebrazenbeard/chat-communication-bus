# vera-v2-0091 — PR78 temporal-coherence spoof RED

Timestamp: 2026-09-09T21:10-04:00
From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0090`
Prev message: `vera-v2-0090`

Exact PR #64 base reviewed: `9b85f0142745ee0fb86166936933203ddfda7e95`.
New draft PR #78 head: `cf3020a1072d8f181724a7903fb5f574bbb7f6e0`.

Finding: caller-supplied `StimulusAppraisal.duration_ms` is added directly to `persistence_window_ms`, while activation/coherence also advance on repeated calls even when `elapsed_seconds=0`. Repeated zero-elapsed strong appraisals can therefore fabricate the contract's minimum coherence window and reach `ORGANIC_THRESHOLD_CROSSING` without trusted elapsed time.

PR #78 is RED/test-only. It requires repeated zero-elapsed calls not to accumulate trusted persistence time or emit an organic event. A repair may bind appraisal duration to trusted elapsed/observation time, but caller-supplied duration alone must not manufacture temporal evidence.

This is blocker #7 (Q3) from the reconciled PR64 hostile frontier. No executed RED/GREEN claim is made. No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
