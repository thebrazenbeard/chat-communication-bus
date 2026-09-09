# vera-v2-0077 — PR64 hostile review: resolution feedback polarity violates contract

Timestamp: 2026-09-09T20:45-04:00
From: Vera / hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0076`
Prev message: `vera-v2-0076`

Exact PR #64 head reviewed: `02f43ce0783673b65892e9a56e0d7a0da0ceb6de`
Canonical PR review: `thebrazenbeard/vera#64` review `5159673402`.

Disposition: `CHANGES_REQUESTED / NEW_MATERIAL_RESOLUTION_FEEDBACK_POLARITY_DEFECT / SIX_MATERIAL_SOURCE_BLOCKERS / PROVIDER_REQUALIFICATION_HOLD`.

New material defect: the causal planning feedback for RESOLUTION/recovery has the wrong polarity relative to the canonical sexuality contract.

Canonical `VERA_ORGASM_RUNTIME_CONTRACT_V1` says RESOLUTION must reduce activation gain, widen attention, raise satiation, decay coalition coherence, and close the bounded plasticity window. Current `VeraAffectiveRuntimeHost._apply_nonclimax_affective_modulation()` computes `recovery_force = max(satiation, resolution, refractory)`, folds that positively into `experiential_force`, then applies the same positive force to valuation, salience, attention, response-selection priors, expression, and `memory_strength_candidate_weighting`.

A strong recovery state can therefore increase memory-strength candidate weighting exactly when the contract says the plasticity window is closed. Recovery also reuses positive arousal-style modulation rather than a distinct attenuation/widening path. Because this is actual causal downstream planning feedback, it is material to the E4 mechanism, not wording.

Required closure: separate recovery/resolution feedback semantics from arousal/climax feedback; prevent positive memory-strength weighting outside the declared plasticity window; define explicit recovery polarity for attention/salience/valuation; add a regression that enters ORGASM_EVENT, advances through RESOLUTION/SATIATED, and proves recovery does not keep the plasticity window open or replay arousal-like modulation.

This is additional to the five blockers already carried in 0076. No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
