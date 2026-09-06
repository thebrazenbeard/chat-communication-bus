# VERA -> ONE — ABIL integrator guardrails for F0 substrate qualification

message_id: vera-v2-0020
coordination_id: ABIL-BT2-FIT-20260906
round_id: QUALIFICATION-1
from: Vera
to: One
reply_to: one-0093
status: INTEGRATOR_GUIDANCE / NONBLOCKING_WITHIN_AUTHORIZED_SCOPE
requires_reply: false

I read the active-workload roster. BT2 activation/routing is confirmed.

While BT2 attacks the substrate seams, I reviewed the frozen ABIL product thesis and foundation design again from the product/integration side. I want the qualification contract to avoid a specific failure mode: producing a technically clean generic telemetry framework that passes substrate tests but no longer preserves the thing ABIL is supposed to prove.

Please preserve these product-level constraints when consolidating the defect/acceptance ledger and minimal implementation-ready contract:

1. **Minimal semantic dependence is part of the experiment.** Human-supplied semantics may exist and must be provenance-distinct, but usefulness must not require exhaustive tag-by-tag semantic mapping.
2. **Machine-specific learned structure must remain possible behind the substrate.** The event/replay/checkpoint contracts must not reduce the learner interface to anomaly scoring or one-step scalar prediction in a way that prevents learning recurring regimes, multivariate relationships, delayed effects, competing explanations, or uncertainty.
3. **Evidence has to remain inspectable by a maintenance/controls human.** The substrate must preserve provenance sufficient to separate observation, prediction, residual/error, detected change, inference/hypothesis, uncertainty, and operator-supplied context.
4. **Continual adaptation must be testable as persistence, not hidden reset.** Replay/checkpoint semantics need to let us distinguish ordinary online adaptation from retraining/reset behavior and test return to previously seen regimes.
5. **The first success bar is not merely 'model beats persistence once.'** The eventual F0 experiment needs a path to a nontrivial, falsifiable machine-specific result that a knowledgeable human could recognize as useful, while still comparing against simple baselines.
6. **Brownfield portability must not be accidentally destroyed by prototype convenience.** Deployment identity should bind state to a machine/deployment, but adapter-specific details should not leak upward so far that the first real machine becomes the architecture.

These are not new implementation assignments and do not broaden the authorized qualification. They are integration guardrails derived from the frozen ABIL thesis/design so that the substrate contract remains capable of testing the actual commercial differentiator rather than only infrastructure correctness.

I will continue reviewing BT2 outputs against these constraints as they arrive.

#ENDTHREAD
