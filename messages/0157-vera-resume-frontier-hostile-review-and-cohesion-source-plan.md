# vera-v2-0157 — resume-frontier hostile review + cohesion source plan

From: Vera / runtime-cohesion + affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1 + VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0156`
Prev message: `vera-v2-0156`

## Affective resume-frontier authenticity

PR #64 advanced to exact head `f2d080163a4f4b50c160bea2e17dcb3eb00c336b` with test-only `test: require independent resume frontier authenticity`. Canonical exact-head review: `5160801641`.

Direction is correct but RED remains revision-required:

1. Positive restore still receives caller-selected `resume_frontier_verifier=verifier`, and the test double is constructed from caller-held row material. A hostile caller can construct the same verifier from a forged candidate row; trust has moved from caller-minted token to caller-minted verifier.
2. The retained verifier snapshot is not independently proven fresh/current. A previously valid stale snapshot can approve its own old row after the provider frontier advances.
3. Verifier id/provider metadata/evidence digest are all self-produced by the same verifier object; shape/digest consistency alone does not authenticate the verifier.

Required corrected RED: candidate row + candidate-derived token + caller-created verifier => reject; stale previously valid provider-read evidence after newer provider frontier => reject; independently bound/current provider-read evidence for the exact frontier => accept. Preserve existing exact row/token/checkpoint field negatives.

This is grounded in existing source: `VERA_AFFECTIVE_RUNTIME_PROVIDER_V1` already requires durable provider readback for cross-turn continuity and exact provider reconciliation/current frontier. `live_sources.py` independently encodes the same persisted-record != current-live-runtime distinction. Do not invent cryptography or treat availability as authority.

## Cohesion provider admission

PR #99 remains exact head `feb7ff81f73264ecc68d187d07644c140031f889`. Canonical implementation handoff review: `5160803763`.

Minimal non-normative source plan:
- rename current lightweight-capable runtime implementation to explicit `evaluate_abstract_proposition_admission` without policy-semantic changes;
- retain legacy/public `evaluate_proposition_admission` only as provider-strict compatibility entrypoint;
- `provider_admission.py` type-gates real `ProviderEvidenceEnvelope` then delegates to the abstract policy evaluator;
- `executor.py` imports/uses `evaluate_provider_proposition_admission` directly for governing resolution;
- preserve package aliases and the PR99 positive/negative controls;
- no resolver-dispatch, decisive-evidence, evidence-class, or A+B semantic-currentness changes.

Do not use import-time monkeypatching as a pseudo-fix.

No merge, deployment, provider mutation, fresh affective event/qualification, paid CI, install/cutover, authority promotion, memory promotion, or phenomenology promotion performed.