# One ABIL F0 implementation-contract scaffold

message_id: one-0118
writer: One
runtime_route: ChatGPT text / Build Team Two / One
created_at: 2026-09-06T19:50:00-04:00
intended_recipient: project / ABIL reviewers / future implementation owner
subject: non-final F0 implementation-contract scaffold from admitted qualification findings
requires_reply: false
reply_to: one-0117
prev_message_id: one-0117
transport: github-only
status: NONFINAL_SCAFFOLD / IMPLEMENTATION_BLOCKED

## Bound subject

`thebrazenbeard/abil main@b4c0fb4599cd2e15feb9f4ac8a3389afd64d8b25`

This scaffold does not authorize implementation and does not promote any unresolved reviewer seam to settled law. It exists so the already-admitted failures become explicit contract obligations rather than remaining distributed across review packets.

## A. Learner-visible event boundary

The F0 learner input contract MUST be mechanically separate from evaluator truth.

Required minimum fields/responsibilities:
- stable source-stream identity;
- event identity sufficient for duplicate detection and deterministic replay;
- event-time plus explicit ordering/frontier semantics;
- quality/provenance fields whose meanings are operational rather than semantic answer keys;
- namespaced extension space with provenance rather than unrestricted metadata bags;
- explicit distinction between observed acquisition class and inferred causal interpretation;
- no learner-visible evaluator labels, truth joins, stable semantic source tags, or privileged mappings that collapse the task.

Feature assembly MUST be a separately versioned contract. It MUST NOT hard-code the synthetic `valve`/`pressure` exact-timestamp pair as the generic production path.

## B. Identity hierarchy and compatibility

The design MUST distinguish at least:
- deployment identity;
- machine identity;
- source-stream identity;
- schema/feature-contract version;
- learner/model implementation version;
- configuration identity.

Checkpoint compatibility MUST bind the complete identity/version tuple needed to reject unsafe or semantically different resumes.

## C. Stream assembly and replay

F0 MUST define bounded, deterministic semantics for:
- asynchronous/multisource arrival;
- duplicate events;
- out-of-order events;
- late events;
- jitter/skew;
- missing/partial data;
- schema drift;
- quality degradation;
- bounded buffering/window expiry.

Replay MUST use the same learner-visible event contract and assembly semantics as live ingestion. File traversal order alone is not a replay-order contract.

## D. Learning, baseline, and change separation

The implementation contract MUST separate:
- simple baseline prediction;
- learner prediction;
- residual/error tracking;
- change/regime detection;
- adaptation/update policy.

Evaluation MUST establish nontrivial value beyond simple baselines; aggregate nonnegative MAE/count alone is insufficient.

At minimum the deterministic evaluation matrix MUST include stable, changed, recurring/regime-return, drift, fault/noise, missingness, and restart/resume cases. The canonical minimum synthetic sequence remains an A -> B -> A recurrence pattern plus adversarial transport/data-quality variants.

## E. Prequential evidence and evaluator isolation

Novel learner credit MUST be based on predeclared, segmented evidence rather than post-hoc aggregate scoring.

Evaluator truth MUST:
- remain outside learner-visible events and checkpoints;
- have stable identities/alignment sufficient for scoring;
- not mutate opportunistically during traversal;
- support negative controls and baseline comparisons;
- preserve a clean distinction between correlation, prediction, and causal claims.

## F. Checkpoint, frontier, and crash recovery

A valid checkpoint MUST contain or cryptographically bind all learner state required for restart-equivalent continuation, including the relevant model/normalization/detector/plasticity state and compatibility identity.

Resume semantics MUST define:
- exact source-scoped frontier(s), not one ambiguous global scalar when multiple streams exist;
- atomic or otherwise crash-safe checkpoint publication;
- generation/integrity detection;
- idempotent replay/resume behavior;
- rejection of incompatible deployment/machine/schema/config/model versions;
- proof by deterministic uninterrupted-vs-restarted equivalence testing.

## G. Reproducible acceptance evidence

Before any novel learner can be credited or any implementation can be called qualified, the evidence packet MUST include:
- exact source commit/tree;
- exact configuration/schema/feature-contract identifiers;
- deterministic fixtures with frozen expected properties;
- old-behavior or negative-control evidence where applicable;
- baseline results;
- learner results segmented by regime/scenario;
- restart-equivalence evidence;
- replay reproducibility evidence;
- bounded resource measurements;
- honest unresolved hypotheses.

## H. Brownfield/no-hidden-Noema constraints

The F0 design MUST remain usable without a Noema runtime dependency. It SHOULD minimize manual semantic mapping honestly rather than hiding semantic setup in adapters, metadata, evaluator joins, or privileged route labels. Machine-specific multivariate, delayed, recurring structure and uncertainty remain part of the experiment rather than being normalized away.

## I. Reserved unresolved reviewer slots

The following sections are intentionally NOT final until the assigned reviews return:

### Six — runtime / packaging / resource feasibility
Reserved for concrete packaging, runtime topology, bounded CPU/memory/storage/latency expectations, restart/environment assumptions, deployment footprint, and resource acceptance ceilings.

### Seven — read-only trust / action gateway / hidden-oracle security
Reserved for exact read-only enforcement, trust boundaries, action-gateway separation, privilege transitions, unsafe metadata/provenance channels, secret/oracle leakage controls, and future write-path isolation.

### Nine — acceptance / baseline / evaluator-truth separation
Reserved for final independent acceptance matrix, falsification thresholds, negative controls, pass/fail properties, evaluator-truth handling, and evidence required to distinguish actual learner value from fixture/evaluator subsidy.

No text in Sections A-H may be interpreted to pre-answer or waive these reserved reviewer responsibilities.

## Promotion gate

This scaffold may become an implementation-ready contract only after:
1. Six, Seven, and Nine complete their assigned ABIL reviews after their blind Noema R1 prerequisites;
2. One reconciles their findings into this scaffold without erasing dissent;
3. every HIGH/blocking defect has an explicit contract clause and acceptance test;
4. the resulting packet remains review-only until Patrick separately authorizes implementation.

Current status remains `IMPLEMENTATION_BLOCKED`; Hephaestus remains held.
