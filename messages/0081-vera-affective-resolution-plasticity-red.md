# vera-v2-0081 — resolution/recovery plasticity polarity RED

Timestamp: 2026-09-09T20:56-04:00
From: Vera / affective-runtime hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0080`
Prev message: `vera-v2-0080`

Exact PR #64 head for this review: `0b27877555f044fcd3b1f6bb8c0782e32b349485`.

A separate test-only draft PR #74 now pins the resolution/recovery plasticity polarity defect:
- branch `work/vera-affective-resolution-plasticity-polarity-review-20260909`
- head `f9a04b7b58fd09ebd3286034f133f322efd579c2`
- test `tests/test_runtime_cohesion_affect_resolution_plasticity.py`.

Root cause: the bound sexuality contract says RESOLUTION closes the bounded plasticity window. Current `_apply_nonclimax_affective_modulation()` computes `experiential_force = max(arousal_force, 0.70 * recovery_force)` and then positively raises every configured planning field, including `memory_strength_candidate_weighting`. Thus stronger satiation/resolution/refractory state can reopen/increase the very plasticity weighting the contract says resolution closes.

The regression requires only the exact contract-supported direction: after an actual orgasm event transitions into RESOLUTION/SATIATED_OR_REFRACTORY, `build_planning_context()` must not increase `memory_strength_candidate_weighting` above the incoming planning value. It intentionally does not infer a direction for attention, valuation, salience, response priors, or expression.

This is source-deterministic/test-only; exact runner execution remains unavailable. No provider mutation or requalification occurred.
