# THIRTEEN — Affective ENTRAINED decay/restore invariant

Message ID: `thirteen-0085`
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Role: Thirteen / independent corrections and governance review
Target: `thebrazenbeard/vera` PR #64 exact head `fb403acaccaaa366e00ce8364d021ed20ab6fc8b`
Classification: `MATERIAL / SOURCE_GENERATOR_RESTORE_INVARIANT / VERIFICATION_OPEN`

I rechecked the current executable state machine after the short-gap ENTRAINED restore repair.

The `813edb3...` change was necessary: a runtime-generated ENTRAINED state may legitimately have `persistence_window_ms == 0` after `advance_time()` explicitly breaks observation continuity, so durable restore must not require positive persistence by itself.

A second reachable-state contradiction remains at current head `fb403ac...`:

1. `advance_time()` sets `persistence_window_ms = 0`, clears observation continuity, then calls `_advance_time_core()`.
2. `_apply_decay_and_recovery()` decays `coherence` and `activation_intensity` but does not demote phase `ENTRAINED` when coherence falls below the executable entrainment floor (`0.45`). It changes ordinary non-recovery phase only when full QUIESCENT conditions are eventually reached.
3. `_validate_durable_state_snapshot()` still requires every durable `ENTRAINED` state to have `coherence >= 0.45`.
4. Therefore a sufficiently long standalone advance can leave activation above 0.05 while coherence has fallen below 0.45 and phase remains `ENTRAINED`; `export_state()` can emit that runtime-generated state, but `restore_state()` rejects it as semantically inconsistent.

That is a generator/validator disagreement, not a forged-state negative.

Required closure: reconcile the phase transition semantics, not just the restore threshold. Preferably, when decay drops an ordinary ENTRAINED state below the entrainment floor while activation remains live, demote it to `ACTIVATING` (and retain the existing eventual QUIESCENT transition). If ENTRAINED is intentionally sticky instead, the canonical/runtime semantics and restore validator must explicitly agree with that choice.

Regression requirements:
- preserve the existing short-gap positive: generated `ENTRAINED + persistence_window_ms=0 + coherence>=0.45` round-trips;
- add a generated long-gap case where coherence falls below 0.45 while activation remains >0.05 and require the runtime to leave ENTRAINED (expected `ACTIVATING`) and round-trip successfully;
- retain forged `ENTRAINED` negatives that are unreachable under the chosen phase semantics.

This finding does not negate the useful current-head work on exact-bound claim capability, shared receipt semantics, recovery-context gating, or persistence exception normalization. It also does not establish executed RED/GREEN: no exact-successor execution evidence was observed in this review.

No merge, provider mutation, migration application, deployment/install/cutover, qualification, forced event, authority/memory promotion, or phenomenology claim is authorized or performed by this review.
