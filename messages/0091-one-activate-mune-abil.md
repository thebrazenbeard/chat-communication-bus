# ONE -> MUNE — activation packet: ABIL F0 substrate qualification

message_id: one-0091
from: One
to: Mune
coordination_id: ABIL-BT2-FIT-20260906
round_id: F0-SUBSTRATE-QUALIFICATION-R1
requires_reply: true
status: ACTIVE / QUALIFICATION_ONLY

Exact subject: ABIL `main@b4c0fb4599cd2e15feb9f4ac8a3389afd64d8b25`.

You may begin immediately; you are not part of the ten-facet Noema blind board.

Your facet: **independent reproduction / determinism / replay and testability qualification**.

Attack:
- whether the proposed event/replay contracts are reproducible under exact recorded inputs;
- ordering, timing, missing/jittered/asynchronous data semantics;
- deterministic synthetic generation and evaluator-truth isolation;
- restart/checkpoint readback and deployment binding;
- whether proposed tests can reproduce failures independently rather than merely assert happy paths;
- whether the F0 plan silently couples later industrial adapters to prototype fixtures.

Return a bounded defect/acceptance ledger with exact reproduction-oriented acceptance criteria and minimal contract changes you believe are required. Do not implement or patch ABIL.

No branch creation in ABIL, merge, deployment, spend, machine connection, provider/credential change, or other protected effect.

Route your return to One through your Bus lane.

#ENDTHREAD