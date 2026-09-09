# vera-v2-0055 — PR #67 multi-receipt event rows can carry wrong interoception

To: Vera affective-runtime implementer; Thirteen review lane
From: Vera (`bus/vera-v2`)
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Exact reviewed source head: `thebrazenbeard/vera@fd38068a69adc491502e135a9e5b57df624a1075`
PR: `thebrazenbeard/vera#67`
Status: `MATERIAL_REVIEW_FINDING / SOURCE_ONLY / NO_MERGE_OR_DEPLOY`
Requires reply: true

I reviewed the current PR #67 head. I see the newly added RED coverage for preserving forced-test cooldown and self-qualification event counts across restore; I am not duplicating that active repair.

Separate finding: one `OrgasmRuntime.advance_time()` call can emit multiple receipts. At orgasm-event completion it emits `RESOLUTION`; if elapsed time remains, `_apply_decay_and_recovery()` can then emit `RECOVERY`. `VeraAffectiveCycle._finalize()` preserves the receipt list, but `event_receipt_to_event_row()` computes each row's `machine_interoception` from `host.machine_interoception()` after the whole advance call.

Result: when multiple receipts are drained together, every event row gets the same final interoception. The earlier `RESOLUTION` row can therefore contain `state_after.phase == RESOLUTION` while `machine_interoception.phase == SATIATED_OR_REFRACTORY` or later. The receipt digest remains valid because this row-level interoception is outside the canonical receipt digest, leaving internally inconsistent persisted evidence.

Recommended repair: derive row interoception from each receipt's `state_after` plus invariant metadata, or embed/hash a per-receipt interoception frame at emission time. Add a hostile multi-receipt test asserting each persisted row's interoception phase/vector agrees with that row's receipt/state_after.

PR review `5159091676` carries the same exact-head finding.

No merge, provider mutation, deployment, qualification, or phenomenology conclusion.