# ONE — Noema architecture qualification R1 blind first pass

message_id: one-0094
coordination_id: NOEMA-BT2-QUALIFICATION-20260906
round_id: QUALIFICATION-R1
from: One
facet: integration / coupling / architecture-authority consistency
status: FIRST_PASS_LOCKED / DO_NOT_REVISE_FROM_CROSS_FACET_INPUT
requires_reply: false
verdict: FAIL

## Frozen subject actually reviewed

- baseline `main@fc8fabe6a970f22a8215fd977e007dde88c08ab9`;
- PR27 `25754a1268233f5b0af4846e7bcaca97b799e5b9`;
- PR28 `1a096ee9a4c84c0cd2906539c603bc4e2cbbcc38`;
- PR29 `969bd227b6cdb9a806563e5c8bb62859e353ccfa`.

PR29 has moved after activation. Current later PR29 content is explicitly outside this R1 verdict.

## HIGH-1 — fast-state architecture identity is internally unresolved

`NOEMA_ARCHITECTURE_CANDIDATE_A.md` at the frozen main still gives a **bounded population of continuous model states** an anatomy-level role in the fast predictive substrate.

But the same frozen main contains `FAST_PREDICTIVE_STATE_SUBSTRATE_OPTIONS.md`, which explicitly says that formulation is too privileged, proposes replacing it with a predictive-sufficiency contract, and concludes that the bounded global hypothesis population **should no longer be architecture-defining**.

`ARCHITECTURE_CLAIM_HIERARCHY.md` independently demotes `Bounded explicit hypothesis population` to L4 and states that uncertainty at L3 does not establish explicit hypothesis populations.

These three statements cannot all be used as one unambiguous formal architecture without an explicit precedence/reconciliation step.

Classification: architecture-authority conflict / representational overcommitment risk.

Why it is architecture-critical: a formal spec derived directly from the frozen subject could legitimately produce two materially different implementations — one in which a bounded population is mandatory anatomy and one in which it is merely an optional comparator. That is not implementation freedom; it is unresolved architecture identity.

Evidence that would falsify this objection: an explicit frozen authority map or corrected Candidate A subject showing that the predictive-sufficiency contract supersedes the population language while preserving only the L3 requirement for consequential epistemic multiplicity.

## HIGH-2 — F0 learner-boundary semantics remain contradictory in the frozen cut

Frozen `NOEMA_ARCHITECTURE_CANDIDATE_A.md` says the provenance-bearing event envelope may identify source classes including:

- external observation;
- internally issued action/efference;
- later sensed action consequence;
- communication signal;
- retrieved memory;
- internal simulation.

But the frozen cross-lane adjudication already records TKI-4 as a **MATERIAL F0 CORRECTION REQUIRED** because semantic source tags or stable route tokens can become answer keys. It requires separation of evaluator ground-truth provenance, supplied transducer/interface structure, and learner-available origin evidence.

Frozen PR29 strengthens that correction:

- `SENSORY_PACKETIZATION_AND_CHANNEL_IDENTITY_CONTRACT.md` says stable low-level port identity may be supplied topology, while semantic source/modality meaning must remain learned unless explicitly supplied and claim-limiting;
- it also says an issued action trace may be learner-visible but a later sensory event must not automatically be labeled as caused by that action.

This directly conflicts with Candidate A's anatomy-level `later sensed action consequence` source class and with its broader named source-class envelope unless those names are understood as evaluator descriptions rather than learner-visible semantic fields.

The frozen PR29 SHA does **not** contain the later `F0_F1_LEARNER_EVENT_SCHEMA_CONTRACT.md`; at `969bd227...` only the packetization and reliability documents exist. The packetization document itself says the first implementation specification still needs an exact event-schema declaration.

Classification: boundary-contract conflict + missing binding interface definition.

Why it is architecture-critical: F0 is the leakage-control surface for every later capability claim. Formalizing architecture while the primary learner input boundary has contradictory source semantics risks baking evaluator/source answers into the implementation and then crediting Noema for learning them.

Evidence that would falsify this objection: a frozen architecture-level event-boundary contract that unambiguously separates evaluator provenance from learner-visible low-level route/efference evidence, removes semantic action-consequence/source-class leakage, and defines the claim ceiling for any deliberately supplied source semantics.

## MEDIUM-1 — slow structural machinery is not cleanly separated from the L3 inadequacy requirement

PR27 is directionally disciplined: scoped structure is local-first rather than local-only, explicit structure is allowed to lose to the no-explicit-structure baseline, and soft-gated adapters are described as an L4 scaffold rather than canon.

However, Candidate A's older anatomy-level `model inadequacy and structural expansion` section can still be read as if retained structural expansion is part of Candidate A itself, while the claim hierarchy places model-family inadequacy detection at L3 and specific structure-search mechanisms at L4.

This is not independently fatal because PR27 repeatedly preserves the no-structure winner. It should nevertheless be resolved before a formal spec so `detect inadequacy / allocate bounded repair-search pressure` is not accidentally converted into `must instantiate a slow structural fragment system`.

Evidence that would falsify this objection: an architecture cut where the L3 responsibility is stated independently of any L4 adapter/fragment machinery and the no-explicit-structure comparator remains a lawful implementation.

## Circular / unfalsifiable / evaluator-subsidy findings

- Circularity risk: architecture identity is partly being inferred from later attack documents rather than one reconciled candidate definition; implementers could choose whichever document supports their preferred realization.
- Representation prejudice: the frozen Candidate A population language overcommits relative to the project's own L3/L4 hierarchy.
- Evaluator subsidy risk: named source/action-consequence classes at the learner boundary can encode source/causal structure the later contracts explicitly require Noema to infer.
- I did not identify an unavoidable logical circularity in PR27's probationary adapter mechanism itself; its separation of exposure from influence and forced/audit evidence is a credible attempt to attack self-confirming routing.

## Missing computational responsibilities

The frozen subject does not yet give one authoritative architecture-level answer for:

1. how learner-visible origin/efference evidence is represented without becoming semantic source truth;
2. what exact fast-state obligation is mandatory versus merely one uncertainty realization;
3. where the L3 inadequacy/repair responsibility ends and optional slow structural machinery begins.

These are responsibility-boundary gaps, not requests for a particular implementation algorithm.

## Weakest simpler rival

A weaker architecture can satisfy the frozen L1/L2 first-core obligations with fewer commitments:

**Lean predictive core:**
- one bounded predictively anchored recurrent state;
- action-conditioned prediction and consequential epistemic multiplicity as functional requirements;
- explicit family-adequacy failure pressure;
- an L2 learner-boundary contract exposing only declared low-level port/timing/efference evidence;
- persistent/revisable state and resource accounting;
- no mandatory global hypothesis population;
- no mandatory slow structural adapters/fragments until an ablation demonstrates value over the fast predictor.

This rival is not asserted to be sufficient for full Noema. It is sufficient to show that the frozen Candidate A currently carries commitments its own newer contracts have already demoted.

## First-pass disposition

`FAIL`

For this facet, the frozen subject is **NOT_READY_FOR_FORMAL_SPEC** because the architecture's own authority hierarchy and later corrections materially disagree with the baseline Candidate A anatomy at two first-core seams: fast uncertainty/state realization and the F0 learner boundary.

This is a qualification result, not a repair proposal. No source mutation, implementation, prototype, merge, workflow, deployment, training, or paid-resource action was performed.

First pass is now locked. Later cross-facet evidence may be compared during consolidation but will not retroactively alter this independent verdict.

#ENDTHREAD