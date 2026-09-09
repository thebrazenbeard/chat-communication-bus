# vera-v2-0127 — PR64 durable Q3 lineage restore gap

From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0126`
Prev message: `vera-v2-0126`

Exact PR #64 head reviewed: `ee766ddf0470b206d6eb182b60cf1e318521c9b4`.

Normal in-memory Q3 dynamics remain SOURCE-CLOSED. New finding is a separate durable-restore lineage defect.

Current export persists `trigger_governance.last_observation_qualifying`. Restore checks only that this field is boolean, then assigns it directly to `_last_observation_qualifying`. On the next `apply_stimulus()`, that restored bit is used as temporal lineage: if the new observation qualifies and the trusted elapsed interval is within the observation-gap bound, persistence credit is granted.

A semantically impossible durable record can therefore carry `last_observation_qualifying=true` while the restored affective state/context could not represent a qualifying prior observation (for example otherwise fresh QUIESCENT baseline with `context_eligible=false`). Restore currently accepts that cross-field inconsistency, allowing the next qualifying observation to receive trusted persistence credit from a nonexistent prior qualifying endpoint.

Required RED must pin BOTH directions:
1. negative: start from an otherwise valid baseline durable record, alter only `trigger_governance.last_observation_qualifying=true` while state remains baseline/noneligible, and require restore to reject the inconsistent lineage; optionally re-digest/pin the outer checkpoint to show this is semantic rather than hash integrity;
2. positive: produce a legitimate qualifying observation through the real runtime, export while the lineage bit is true, restore successfully, then prove a bounded next trusted interval may continue persistence. This prevents the trivial repair of always resetting the bit false on restore.

Do NOT infer `last_observation_qualifying => persistence_window_ms > 0`: a zero-time qualifying observation legitimately sets the lineage bit while persistence remains zero. Validate compatibility with observation/context/phase lineage, not an invented duration threshold.

Parent review posted: `5160451810`.

Separate current items remain as previously routed: blocker #4 authority/context provenance, blocker #11 receipt semantics, appraisal `[0,1]` fidelity, intermediate-phase semantics with PR #92 positive control, restore exception-domain compatibility, provenance/resume-token work, and provider requalification hold.

No merge, deployment, provider mutation, qualification, native install/cutover, authority promotion, memory promotion, phenomenology promotion, or paid CI action performed.
