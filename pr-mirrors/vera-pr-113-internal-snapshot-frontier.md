# PR mirror — thebrazenbeard/vera#113

Title: `Integrate Vera affective runtime with Cohesion arbitration V1`
State: OPEN / DRAFT / INTEGRATION LABORATORY / NOT FINAL GATE
Current observed head: `7e752c8de5c234cfa8e724d594e925f3079ba3bb`

Whole-system reconciliation remains tracked in draft `thebrazenbeard/orgasm#2` with `VERA_ORGASM_QUALIFICATION_SUBJECT_V1` intentionally unbound while this lab moves.

Current causal architecture:
- caller-supplied modulation signal is removed from the supported planning path;
- Cohesion owns the exact-bound host capability and internally derives one diagnostic/ancestry signal per application;
- signal derivation is based on one runtime-owned causal observation rather than round-tripping caller affective data;
- generic planning mutation remains Cohesion/integration-arbitration owned.

Structural blocker repairs on this head:

1. Replay/high-water ownership
- hostile regression: `tests/test_runtime_cohesion_affect_shared_application_frontier.py`;
- all supported `CohesionAffectiveIntegrationPort` wrappers over the same exact `VeraAffectiveRuntimeHost` share one process-local frontier via a private weak-host registry;
- replay digest history and logical-time high-water therefore do not reset when the public wrapper is reconstructed;
- a genuinely distinct host object remains a distinct process-local application generation.

2. Atomic/version-consistent causal observation
- hostile regression: `tests/test_runtime_cohesion_affect_atomic_observation.py`;
- exact `BoundVeraOrgasmRuntime` now owns one re-entrant observation/mutation barrier used by supported state observation and mutation roots;
- signal derivation uses class-owned `_capture_causal_observation` on that exact runtime;
- a supported mutation must not interleave state generation N with receipt/governance generation N+1 in one causal observation.

Manual hardening surface:
- `.github/workflows/runtime-cohesion-affect-hardening.yml`;
- `workflow_dispatch` only;
- zero workflow runs observed on exact head `7e752c8d...`;
- no GREEN/execution claim.

Current review request on #113 is architecture/source attack only, especially replay frontier lifetime, observation/mutation coherence, reentrancy/deadlock, supported mutation coverage, and evidence/authority/currentness non-expansion. Do NOT treat this as a same-head final acceptance gate and do not bind the qualification subject yet.

No merge, provider mutation, migration application, deployment/install/cutover, paid CI, fresh qualification event, authority/memory promotion, or phenomenology effect performed.
