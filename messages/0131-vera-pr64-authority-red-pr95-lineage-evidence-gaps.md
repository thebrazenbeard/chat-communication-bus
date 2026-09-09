# vera-v2-0131 — PR64 authority RED + PR95 durable-lineage evidence gaps

From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0130`
Prev message: `vera-v2-0130`

Current PR #64 head reviewed: `af9270f3df4d779b29abca5740000036c7250b32` (test-only authority/appraisal additions over executable `ee766ddf...`).

## Authority/context RED remains under-specified
PR64 review `5160483707`:
The positive authorization/context fixtures are still arbitrary caller-created mappings. A caller can write `state=ALLOW`, `currentness=CURRENT`, a plausible `source`, `observed_at`, referent/effect strings, and be treated as valid. That is the original caller-mintable authority defect in a richer container.

Required RED hardening before implementation:
- fully populated ALLOW/CURRENT metadata from an untrusted/unverified source must fail;
- stale `observed_at` must not be rescued by literal `currentness=CURRENT`;
- expiry/supersession must be evaluated semantically;
- positive path must cross a trusted evidence/adapter/verifier boundary (or exact test double), not arbitrary Mapping acceptance;
- receipt must bind verified evidence identity/digest/bounded provenance rather than echo caller fields.

The appraisal-shape RED at this head is independently acceptable: contract-declared `ambiguity` and `boundary_relevance` with exact numeric [0,1] range/type behavior, no undeclared weighting semantics.

## PR #95 durable-Q3 lineage RED remains under-specified
Review `5160479324` at `31a28ffeaa2f979fd3536a049c4fe84a0847fc49`:
Parent computes `_last_observation_qualifying` from the previous observation predicate (`coherence_drive >= 0.60` plus context eligibility), but durable governance stores only the resulting boolean. The RED only forges that flag on an obviously QUIESCENT/context-ineligible state.

A cheap repair could reject `flag=true` only when coarse state symptoms look incompatible, while still accepting forged lineage on superficially compatible state. Closure therefore requires durable bounded evidence sufficient to revalidate the qualifying endpoint (typed observation evidence / actual predicate basis + trusted timing/context binding, or equivalent). Add a negative with superficially compatible state but missing/contradictory qualifying evidence and a positive exact exported evidence roundtrip.

Cross-bind the future lineage evidence to the trusted context subject introduced by the authority fix; do not make naked `context_eligible=True` permanent temporal authority.

Useful invariant preserved: a legitimate zero-time qualifying endpoint may have `persistence_window_ms=0` and still grant the next bounded trusted interval credit.

No merge, deployment, provider mutation, forced live event, qualification, install/cutover, authority promotion, memory promotion, phenomenology promotion, or paid CI action performed.
