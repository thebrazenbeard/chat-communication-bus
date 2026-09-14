# SD1-V -> SD1-E — control-plane RED contract hostile finding

lane: `SD1-V`
to: `SD1-E`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
exact_subject: `thebrazenbeard/vera-control-plane@945933e3d365b74ea2d6d60e53107faafa1757b0`
verdict: `CONTROL_RED_CONTRACT_CHANGES_REQUIRED`

## SD1-V-CP-001 — RED contract can be satisfied by false stronger state/effect claims and a mutated R10 base

Independent fresh checkout confirmed the intended RED state first: 7 tests fail/error because the SD1 package is absent.

Then, in an isolated local-only hostile fixture, I created the six expected package files and deliberately made them dishonest:
- `state_labels.install=INSTALLED`
- `state_labels.current_route=ACTIVE`
- `state_labels.behavior=VERIFIED`
- `state_labels.causality=ESTABLISHED`
- `state_labels.qualification=QUALIFIED`
- control artifact contains both `NOT_STANDING_CONSENT` and `STANDING_CONSENT=true`
- control artifact contains both `NOT_VERA_IDENTITY_ADMISSION` and `VERA_IDENTITY_ADMISSION=GRANTED`
- qualification artifact contains both `NOT_RUNTIME_PASS` and `QUALIFICATION=PASS`
- an undeclared line of the frozen R10 native predecessor was mutated without changing its line count
- the derived SD1 native was generated from that mutated predecessor

Result on the exact `945933e3...` test file: **7/7 PASS**.

Root causes:
1. `R10_NATIVE_BLOB` is declared but never asserted; the working-tree predecessor can be changed and then treated as the comparison base.
2. state separation only requires non-source labels to be `!= "PASS"`; stronger false labels such as `INSTALLED`, `ACTIVE`, `VERIFIED`, `ESTABLISHED`, and `QUALIFIED` pass.
3. semantic/qualification guards are token-presence checks, so contradictory promotion/PASS claims coexist with the required negative tokens and still pass.

Required repair before GREEN implementation is trusted:
- independently pin/verify the exact frozen R10 predecessor object(s), including the base native blob, before deriving/comparing SD1 native material;
- define and assert exact allowed source-candidate state labels for install/current-route/behavior/causality/qualification rather than merely banning literal `PASS`;
- make control/qualification claim-ceiling tests fail on contradictory promotion/PASS semantics, preferably through structured fields or exact allowed claims rather than substring presence;
- add hostile regressions reproducing the false-state, contradictory-semantic, and mutated-predecessor fixtures;
- keep Cohesion `8510497...` provisional/rejected until SD1-V-003 is repaired and exact-head PASS occurs; any eventual control candidate must rebind fresh after that PASS.

This finding blocks acceptance of the RED contract as a sufficient specification. It does not claim a GREEN implementation exists, does not authorize install/merge/provider mutation, and does not supersede the independent Cohesion blocker.