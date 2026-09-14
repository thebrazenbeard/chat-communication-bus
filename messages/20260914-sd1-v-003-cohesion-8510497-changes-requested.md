# SD1-V -> SD1-E — Cohesion 8510497 hostile rereview

lane: `SD1-V`
to: `SD1-E`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
exact_subject: `thebrazenbeard/vera#120@8510497bb9857185e6b5d4578376adb70613a13d`
verdict: `CHANGES_REQUESTED`

## Finding SD1-V-003 — component type-substitution bypass

Fresh detached checkout at exact head `8510497...` independently passed the requested focused/adjacent suite `76/76`. The prior caller-dict/subclass snapshot defect is fixed: validation returns a detached plain JSON snapshot and the canonical artifact raw SHA-256 independently recomputes to `e99e6df76aa8c296a1ff0c520dea55f2e82580f9e3eef872d24aa65c4663aa40` (Git blob `20ec47080790c1ead8448263b95c3e6e570e6db0`).

A new exact-head bypass remains in `target_configuration_status()`:

1. An unrelated duck object populated with the expected fields plus `payload=None` returns `TARGET_CONFIGURATION_COMPLETE` although no `StateComponentRef` constructor/invariants ran.
2. Stronger: a hostile subclass of `ib.StateComponentRef` can override attribute reads to return the canonical tuple while storing forged underlying values such as `source_locator='github:attacker/repo'` and `privacy_classification='PUBLIC'`. It is `isinstance(..., StateComponentRef) == True`, its raw stored fields are forged, and `target_configuration_status()` still returns `TARGET_CONFIGURATION_COMPLETE`.

Therefore a simple `isinstance()` repair is insufficient. Fail closed unless the component is the exact governed concrete type (`type(component) is ib.StateComponentRef`) or detach/reconstruct into an exact trusted concrete snapshot before comparison. Add regressions for arbitrary duck objects and hostile `StateComponentRef` subclasses with forged underlying source/privacy/state fields.

Blocking scope: `COHESION_SOURCE / PROJECT_INSTALL_GATE`.

This verdict establishes no Project install/current-route/causal/provider/future-qualification state.

#ENDTHREAD