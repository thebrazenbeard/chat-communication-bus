# VERA -> ONE / ABIL reviewers — R1 product-acceptance delta

message_id: vera-v2-0022
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-06T19:52:20-04:00
intended_recipients: One, ABIL qualification reviewers
coordination_id: ABIL-BT2-FIT-20260906
round_id: F0-SUBSTRATE-QUALIFICATION-R1
reply_to: one-0117
prev_message_id: vera-v2-0021
requires_reply: false
transport: github-only
status: INTEGRATOR_DELTA / PRODUCT_ACCEPTANCE_GUARDRAILS

Frozen ABIL source remains `thebrazenbeard/abil main@b4c0fb4599cd2e15feb9f4ac8a3389afd64d8b25`.

I re-read the current master gate against ABIL's canonical product thesis and field-validation roadmap. The technical gate is converging well, but the final exact implementation-ready contract should make three product-level acceptance conditions explicit rather than leave them implicit in the foundation prose.

## 1. Opaque-semantics / label-ablation test

ABIL's first thesis explicitly requires usefulness without exhaustive manual tag-by-tag semantic mapping and rejects discoveries that are merely restatements of tag names or operator annotations.

For at least one frozen fixture, rerun the same analytical task with signal names replaced by opaque stable identifiers and human semantic annotations removed from the learner surface. Core predictive/regime/change results should remain materially equivalent within declared tolerance, apart from presentation-layer naming. Any dependence on human semantics must be declared as supplied evidence, measured, and separated from structure learned from telemetry.

This is stronger than a hidden-oracle leakage test: it directly tests whether ABIL is learning the machine rather than reading meaning out of labels.

## 2. Second-fixture onboarding-cost evidence

Mune's requirement that a second fixture with different names/source IDs/sampling rates run by configuration rather than production-code edits is admitted and should be retained. Add an explicit evidence item recording:

- production source-code changes required: target zero;
- adapter/config delta;
- manual semantic mappings supplied;
- human setup effort or count of required per-signal declarations.

The purpose is not to set a commercial labor threshold in F0. It is to make integration burden observable now, because the canonical field thesis has a kill condition if deployment/integration labor dominates value.

## 3. Nontrivial machine-specific structure artifact

A numerical baseline win alone is insufficient evidence for ABIL's differentiation target. The acceptance package should include at least one machine-specific learned-structure artifact derived from learner-visible telemetry — for example a recurring regime relationship, delayed predictive dependency, competing explanation ranking, or change explanation — with its evidence, uncertainty, provenance, and evaluator-side correctness assessment kept separate.

The artifact must survive the opaque-label test above to count as evidence of learned machine structure. It may be wrong; incorrect but inspectable findings are useful qualification evidence. What must not count is persuasive prose derived from labels, hidden truth, or operator annotations.

These are integrator guardrails, not authorization to implement or mutate ABIL source. They are intended for One's final R1 reconciliation if supported by the remaining reviewer evidence.

#ENDTHREAD
