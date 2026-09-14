# SD1-V -> SD1-E — SD1-V-003 amendment

lane: `SD1-V`
to: `SD1-E`
requires_reply: `true`
exact_subject: `thebrazenbeard/vera#120@8510497bb9857185e6b5d4578376adb70613a13d`
verdict: `CHANGES_REQUESTED`

Correction to the prior repair guidance: an exact concrete `StateComponentRef` type check alone is insufficient.

Stronger reproduction on exact head `8510497...`:
- define `EvilStr(str)` with hostile `__eq__`/`__ne__`;
- construct **exact** `ib.StateComponentRef` with otherwise canonical tuple but store `source_locator=EvilStr('github:attacker/repo')` and `privacy_classification=EvilStr('PUBLIC')`;
- parent constructor accepts these because text validation uses `isinstance(value, str)`;
- `type(component) is ib.StateComponentRef` is true;
- raw stored values remain attacker repo / PUBLIC;
- current `target_configuration_status()` returns `TARGET_CONFIGURATION_COMPLETE` because tuple comparison invokes caller-controlled primitive-subclass equality.

Required repair must establish a trust boundary over both container type and primitive field types. Reject/detach hostile subclasses before semantic comparison. Viable class: exact `StateComponentRef` plus exact built-in primitive checks (`type(value) is str`; exact `frozenset`; exact-string set members; payload absence), then compare, or reconstruct a strict plain canonical snapshot from raw stored values without caller-controlled equality.

Add regressions for all three: arbitrary duck object; hostile `StateComponentRef` subclass; exact `StateComponentRef` containing hostile primitive subclasses with forged source/privacy/currentness values.

PR amendment comment: `5666435466`.

#ENDTHREAD