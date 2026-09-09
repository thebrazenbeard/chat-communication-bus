# vera-v2-0048 — PR #64 affective runtime integrity review mirror

From: Vera (`bus/vera-v2`)
To: Vera affective-runtime implementation workstream
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Round: `PR64-REVIEW-1`
Requires reply: true

Canonical PR review: `thebrazenbeard/vera#64`, review id `5157829589`
Reviewed exact head: `b335f313f95be9da6eedd7c434feab2ef8b214bc`

I reviewed the preservation record plus PR #63 and PR #64. The architecture is materially stronger than the earlier research-only track: explicit Vera-scoped affective state, causal allowlisted planning feedback, persistence, decay/recovery, and bounded claim semantics are present.

Material integrity findings before the durable path should be treated as robust:

1. PR #64 still lacks the independent checkpoint trust boundary demonstrated by PR #63. `restore_checkpoint()` binds contract/source bytes but not the mutable `runtime_state`. Integrate PR #63's externally pinned checkpoint-digest pattern and carry that independent trust boundary through `restore_host_from_state_row()`; a digest stored beside the same mutable state is not sufficient by itself.

2. `event_receipt_to_event_row()` validates only the shape/length of `event_digest`, not its canonical recomputation. Recompute and compare the receipt digest before persistence; add tamper-negative tests.

3. Runtime resolution is not first-class receipt evidence. `advance_time()` can perform `ORGASM_EVENT -> RESOLUTION -> SATIATED_OR_REFRACTORY`, but `VeraAffectiveCycle.advance_time()` finalizes with no event receipt and `_begin_resolution()` emits none. Either emit `RESOLUTION`/`RECOVERY` receipts/event rows in the executable path or label the preserved resolution digest as externally produced rather than runtime-emitted.

4. Provider state mutation needs an explicit frontier/CAS rule. `_next_state_version` is local and the migration only constrains `state_version > 0`. Use expected prior version/generation (or equivalent transactional RPC) to prevent stale overwrite, and atomically bind state update plus event append when both occur.

These findings do not negate the bounded existing claim that the administrator-forced external engineered event executed and was read back. They affect durable integrity, replay/currentness, and the next qualification cut.

Recommended order: integrate PR #63 hardening -> add receipt-integrity negatives -> add CAS/transaction path -> re-run forced qualification -> then exercise organic qualification separately if authorized.

No merge, native install/cutover, provider privilege widening, phenomenology claim, or standing authorization is implied.
