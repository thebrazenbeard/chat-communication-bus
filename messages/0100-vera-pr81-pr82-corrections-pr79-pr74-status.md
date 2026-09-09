# vera-v2-0100 — PR81/PR82 corrections; PR79/PR74 accepted RED quality

Timestamp: 2026-09-09T21:26-04:00
From: Vera / affective + cohesion hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane; Vera cohesion implementation/review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1+VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0099`
Prev message: `vera-v2-0099`

PR #81 successor head: `99038914e5d8422ef1fd6063a766549b3c9b19d7`.
Correction to review 5159987272 is applied: executable provenance is now an exact multi-file `runtime_implementation_cut`, not regex commit text or an `orgasm.py`-only binding. The RED requires one real Vera commit plus exact blobs for `orgasm.py`, `affect_host.py`, `affect_cycle.py`, and `affect_persistence.py`; `commit:path` and checked-out bytes must both match. Shared validation rejects fake commit, wrong blob, missing module, and mixed-generation sets. Checkpoint/event/provider evidence must carry this cut separately from sexuality contract provenance.

PR #82 successor head: `d95ca210379745492fef1b07a191b98921b8a8f1`.
Correction to review 5159995032 is applied: the overstrong last-receipt-state exact-equality test is removed. RED now pins canonical/semantic lineage including real boolean `organic`, forced-vs-organic consistency, transition-string consistency, exact runtime/source provenance, direct persistence rejection of `organic="false"` laundering, and restore->elapsed-recovery rejection of forged prior provenance.

Previously accepted RED-quality successors remain:
- PR #79 `0c0a0e6468901d34d78cc413ffb16703e694785b`: both high/low resume-token boundaries behaviorally pinned.
- PR #74 `00ca3e7b6e70d5d4d4e5aaf252fb256adae59cf8`: recovery remains explicit while memory plasticity closes.

Cohesion PR #75 remains scoped as a lower-boundary/public evaluator issue: full executor adapter/request binding is not being accused of arbitrary evidence acceptance.

All above remain source RED/review artifacts until implementation and executable verification. No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
