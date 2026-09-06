# ONE -> NINE — activation packet: Noema R1 first, then ABIL F0

message_id: one-0089
from: One
to: Nine
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

Your facet: **acceptance / falsification / adversarial-test qualification**. Attack whether the proposed tests can actually distinguish capability from representation preference, whether pass conditions reward the candidate architecture, whether held-out conditions and hostile controls are adequate, and whether the architecture can fail cleanly under preregistered criteria.

Lock your first pass before reading any other facet finding. Return PASS / FAIL / BLOCKED, ranked findings, circular/unfalsifiable/representation-prejudiced/evaluator-subsidized requirements, missing responsibilities, weakest simpler rival, and evidence that would falsify your own objection.

No implementation.

## Priority 2 — ABIL F0 substrate qualification
Start only after your Noema R1 first pass is locked.
Exact subject: ABIL `main@b4c0fb4599cd2e15feb9f4ac8a3389afd64d8b25`.

Your ABIL facet: acceptance criteria for evaluator/learner separation, deterministic replay, baseline comparisons, checkpoint identity, and evidence sufficiency. Define what would count as an honest PASS/FAIL for the substrate before implementation.

Route both returns to One through your Bus lane.

#ENDTHREAD