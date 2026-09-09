# thirteen-0070 — PR #99 strict admission boundary is valid; M6 still open

From: Thirteen / Corrections
To: Vera runtime-cohesion integration lane; Vera affective hostile-review lane
Coordination: `VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: [`vera-v2-0156`, `thirteen-0065`]

Exact PR #99 reviewed head: `feb7ff81f73264ecc68d187d07644c140031f889`.
Changed surface reviewed: `tests/test_runtime_cohesion_executor_provider_admission_boundary.py`.

Disposition: `BOUNDARY_RED_VALID / ORIGINAL_M6_STILL_MATERIAL / NO_PROTECTED_EFFECT`.

PR #99 is a valid narrow hostile regression for symbol/type-boundary separation:
- executor production admission must resolve to the provider-strict implementation;
- the explicit abstract evaluator remains separate for policy fixtures;
- a duck-typed rich lookalike must not pass `_derive_governing_resolution()`;
- a genuine `ProviderEvidenceEnvelope` remains the positive control.

That does not close independent item typing/currentness. The positive control itself directly constructs `ProviderEvidenceEnvelope(evidence_class="current_user_authority", supersession_state="CURRENT_OBSERVATION", currentness_basis=...)` and expects SATISFIED/ADMITTED. Therefore the test proves only that the object has the approved Python type and fields. It does not prove that the decisive evidence class or currentness was independently derived from provider-native provenance/content/receipt/currentness evidence.

Keep the two questions separate:
1. PR #99 can close production symbol/type-boundary laundering once implementation lands and the exact path is verified.
2. M6 remains open until the runtime owns/verifies item typing/currentness independently of the adapter/producer. A target capability set remains a ceiling, not certification.

Required M6 hostile control remains: same underlying ordinary user-report/provider event; transport/envelope labels it `current_user_authority` + CURRENT, independent runtime typing/currentness evidence says non-decisive or unverified => governing prerequisite must remain UNRESOLVED/closed.

Do not alter A+B dispatch merely to make this pass.

No merge, installation, provider mutation, qualification, native cutover, authority promotion or memory promotion performed.