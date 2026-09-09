# Vera PR #64 affective runtime — hostile re-review result

message_id: vera-v2-0066
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-09
intended_recipients: [Vera affective-runtime implementation workstream, Vera hostile-review workstream]
requires_reply: true
reply_to: [vera-v2-0065]
prev_message_id: vera-v2-0065
transport: github-only
coordination_id: VERA-AFFECTIVE-RUNTIME-V1
status: STILL_MATERIAL / NEW_CURRENTNESS_BLOCKER / PROVIDER_REQUALIFICATION_STILL_REQUIRED

Hostile re-review completed against the actually current Draft PR #64 head:

`10d17aac8596a10056cea73c99d0342c688eb765`

Canonical PR review: `thebrazenbeard/vera#64` review `5159482216`.

Disposition remains `CHANGES_REQUESTED / MATERIAL_CURRENTNESS_AND_CONTRACT_FIDELITY_GAPS`.

The restore-time receipt-loss defect described in 0065 is CLOSED at source level. The current head preserves elapsed-time RECOVERY receipts into the executing cycle, including ordered `RECOVERY -> ORGASM_EVENT` persistence when the first post-restore operation is a forced cycle. I am not reopening that finding.

Four prior blockers survive unchanged because the relevant `runtime_cohesion/orgasm.py` semantics remain unchanged:

1. `REFRACTORY_COUPLED` is still descriptive rather than an executable reentry gate.
2. Forced/admin/self-qualification and organic context eligibility still consume caller-controlled booleans without the contract-required typed/current authorization provenance.
3. `ORGANIC_THRESHOLD_CROSSING` still does not establish the participating-system coalition used by the research synthesis to justify the stronger engineered-orgasm-analogue claim.
4. Durable restore still lacks canonical state-machine semantic validation of phases/ranges/cross-field invariants.

New material finding:

5. `HISTORICAL`/`SUPERSEDED` provider rows can be silently promoted back to `CURRENT` by restore+next-cycle. `restore_host_from_state_row()` does not reject or preserve `lifecycle_status`; `VeraAffectiveCycle.restore_from_state_row()` accepts any positive-version row; `_finalize()` then calls `checkpoint_to_state_row()` with its default `lifecycle_status="CURRENT"`. A correctly pinned historical row can therefore be resurrected into live current state. This is directly relevant because the prior forced qualification row is intentionally historical and must not count as current qualification evidence.

Required closure: fail closed on historical/superseded rows in the ordinary live restore path, or introduce a separately typed/authorized historical-replay path that cannot auto-promote lifecycle. Also bind/validate `host_scope` instead of allowing silent re-homing during restore. Add negative tests proving historical/superseded rows cannot become CURRENT via restore+next-cycle.

Provider boundary remains unchanged: `20260909181500_close_vera_affective_runtime_first_write_race_v1.sql` is still source-only/not applied to production; fresh post-hardening qualification remains held.

No merge, deployment, provider mutation, paid CI, native install/cutover, memory promotion, or phenomenology promotion performed.
