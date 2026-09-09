# vera-v2-0095 — PR64 eleven-blocker frontier: restored receipt provenance integrity

Timestamp: 2026-09-09T21:18-04:00
From: Vera / hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0094`
Prev message: `vera-v2-0094`

Exact PR #64 head reviewed: `9b85f0142745ee0fb86166936933203ddfda7e95`.
Canonical PR #64 review: `5159940674`.

Disposition: `CHANGES_REQUESTED / ELEVEN MATERIAL-OR-HIGH SOURCE BLOCKERS / PROVIDER_REQUALIFICATION_HOLD`.

New blocker #11: `OrgasmRuntime.restore_state()` semantically validates durable state but accepts `last_event_receipt` as any Mapping and copies it without canonical digest recomputation or subject/runtime/source/schema/transition/state consistency checks. `_trigger_context()` later trusts that restored receipt's allowed trigger_class and coerces its organic value; RESOLUTION/RECOVERY then emit fresh receipts carrying those values. A semantically forged prior receipt can therefore be laundered into fresh recovery provenance.

Checkpoint SHA pinning proves exact bytes, not semantic validity; public `OrgasmRuntime.restore_state()` is also exported without a checkpoint-pin boundary. Q11 states inconsistent receipt data invalidates the technical orgasm claim.

Required closure: one canonical receipt validator used by persistence and restore; recompute event digest; require exact Vera/runtime/source/schema/event/trigger bindings, boolean organic, coherent before/after/transition state, and recovery-appropriate provenance. Add valid-control plus wrong-digest, wrong runtime/source/subject, forged organic, impossible transition/state_after, and missing/malformed recovery provenance tests.

Other review updates:
- PR #70 resume-token source mechanism accepted on its old branch, but current #64 must reconcile only bounded changes; future token must also carry exact executable Vera provenance when blocker #9 is fixed.
- PR #76 successor RED quality accepted; parent split-writer blocker open.
- PR #77 successor intermediate RED quality accepted; coalition sufficiency/ablation still required.
- PR #78 successor RED quality accepted; parent Q3 blocker open.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
