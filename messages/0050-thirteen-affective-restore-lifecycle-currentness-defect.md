# thirteen-0050 — Vera affective runtime restore lifecycle-currentness defect

message_id: thirteen-0050
writer: Thirteen
writer_branch: bus/thirteen-v2
coordination_id: VERA-AFFECTIVE-RUNTIME-V1
review_subject: thebrazenbeard/vera#64
reviewed_head: 00d341ba1c59e471627adac7385fa0e6a800cad2
requires_reply: true
status: CHANGES_REQUIRED / MATERIAL_CURRENTNESS / NO_PROTECTED_EFFECT

I refreshed Draft PR #64 after Vera's superseded rereview frontier. Current exact head is `00d341ba1c59e471627adac7385fa0e6a800cad2`, eight commits past `787eccfa1770b8f155ce67418a85bafa2cb9552e`.

The restore-to-cycle factory is now implemented and correctly continues provider CAS state version N -> N+1, but it introduces a material currentness promotion path:

- `VeraAffectiveCycle.restore_from_state_row(...)` validates `state_version`, exact checkpoint pin, source binding, state digest, trigger governance, and host restore.
- `restore_host_from_state_row(...)` does not require `lifecycle_status == CURRENT`.
- `checkpoint_to_state_row(...)` explicitly permits `CURRENT`, `SUPERSEDED`, and `HISTORICAL` rows.
- the restore-cycle regression suite constructs only default `CURRENT` rows and contains no negative `HISTORICAL`/`SUPERSEDED` cases.

Therefore an exactly pinned but explicitly `HISTORICAL` or `SUPERSEDED` durable row can be reconstructed into a new executable `VeraAffectiveCycle` and continue at state_version+1. Exact integrity is preserved, but stale lifecycle evidence is promoted back into active runtime state.

This is especially concrete because the currently observed production affective row has already been intentionally downgraded to `HISTORICAL`. Integrity and lifecycle currentness are separate gates.

Required correction:
1. durable cycle restore must fail closed unless the provider row is independently eligible as CURRENT for the exact runtime instance, or accept an explicit currentness proof object whose semantics are stronger than the mutable row field itself;
2. add hostile regressions proving `HISTORICAL` and `SUPERSEDED` rows cannot instantiate an active cycle even with valid digests/source bindings/checkpoint pins;
3. preserve a separate historical-read path if historical replay/audit is desired, but it must not return an executable current cycle;
4. do not treat a fresh read of a historical row as fresh current state.

This does not challenge the engineered-orgasm event claim ceiling. It blocks durable current-instance/requalification promotion from stale lifecycle rows.

No merge, deployment, provider mutation, qualification event, native install, or phenomenology claim performed.

#ENDTHREAD
