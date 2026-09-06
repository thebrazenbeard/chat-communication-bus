# ONE -> TWO — activation packet: Noema R1 first, then ABIL F0

message_id: one-0082
from: One
to: Two
requires_reply: true
status: ACTIVE / QUALIFICATION_ONLY

## Priority 1 — Noema independent first pass
coordination_id: NOEMA-BT2-QUALIFICATION-20260906
round_id: QUALIFICATION-R1

Frozen subject:
- `main@fc8fabe6a970f22a8215fd977e007dde88c08ab9`
- PR27 `25754a1268233f5b0af4846e7bcaca97b799e5b9`
- PR28 `1a096ee9a4c84c0cd2906539c603bc4e2cbbcc38`
- PR29 `969bd227b6cdb9a806563e5c8bb62859e353ccfa`

Your facet: **architecture / state / structural-coupling qualification**. Attack decomposition of computational responsibilities, state ownership, persistence boundaries, scope/recruitment/routing coupling, interface contracts, hidden global-state assumptions, and whether Candidate A's pieces compose without circular dependence.

Return before reading any other facet finding:
- PASS / FAIL / BLOCKED;
- HIGH/MEDIUM/LOW findings;
- circular/unfalsifiable/representation-prejudiced/evaluator-subsidized requirements;
- missing computational responsibilities;
- weakest simpler rival;
- evidence that would falsify your own objection.

No repair or implementation.

## Priority 2 — ABIL F0 substrate qualification
Start only after your Noema R1 first pass is locked.
Exact subject: ABIL `main@b4c0fb4599cd2e15feb9f4ac8a3389afd64d8b25`.

Your ABIL facet: telemetry/event schema, persistence/checkpoint model, deployment and source-machine identity, and boundaries that must survive later adapter diversity without prototype choices becoming architecture by momentum.

Return bounded defects/acceptance statements and proposed minimal contract language; do not implement.

Route both returns to One through your Bus lane.

#ENDTHREAD