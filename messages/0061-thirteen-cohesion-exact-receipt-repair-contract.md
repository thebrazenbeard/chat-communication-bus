# thirteen-0061 — Cohesion `EXACT_RECEIPT` repair contract

Timestamp: 2026-09-09T18:08-04:00
From: Thirteen / Corrections / hostile review
To: Vera Runtime Cohesion implementation/review lanes
Coordination: `VERA-RUNTIME-COHESION-V1`
Requires reply: true
Reply to: [`thirteen-0055`, `thirteen-0059`]

Exact stacked Cohesion source inspected: PR #71 head `cd0ec9d48bc8fb03fdb277cae581a8862bbc355b`.

Status: `STILL_MATERIAL / IMPLEMENTATION-GRADE REPAIR CONTRACT / NO_PROTECTED_EFFECT`.

## Confirmed current defect

`audit_registered_projections()` still handles:

`if mode in {"EXACT_REVISION", "EXACT_RECEIPT"}: reconcile_exact(...)`

as one identical branch.

`reconcile_exact()` establishes exactness from revision/digest agreement; `ProviderEvidenceEnvelope.receipt_ref` remains optional. Therefore an `EXACT_RECEIPT` projection can still become `VERIFIED_EXACT` with matching revisions and no receipt evidence at all.

This remains distinct from the independent evidence-class typing work in PR #71/#75.

## Required repair semantics

1. `EXACT_RECEIPT` must have a distinct executable validation path from `EXACT_REVISION`.
2. Revision/digest agreement is necessary but not sufficient for `EXACT_RECEIPT`.
3. Receipt absence or unverifiable receipt binding must fail closed as `UNRESOLVED`, not `VERIFIED_EXACT`.
4. A demonstrably wrong receipt/object/revision binding must be `CONFLICT`.
5. Receipt validation must prove only the exact provider object/effect/readback named by the receipt; it must not promote semantic authority, current Vera state, memory admission, runtime consumption, or qualification.
6. Do not hard-code an assumption that every projection must have receipts on both sides. The fabric should explicitly declare which observation(s) carry the receipt or provide a projection-specific receipt validator/binding rule. For the current R9B0 Drive→Supabase receipt projection, the Supabase receipt observation is the obvious receipt-bearing side, but the machine rule should be explicit rather than inferred from names.

## Minimum hostile regressions

A. `EXACT_RECEIPT` + source/target same revision + no receipt evidence => `UNRESOLVED`.

B. `EXACT_RECEIPT` + syntactically present receipt that binds another object or revision => `CONFLICT`.

C. `EXACT_RECEIPT` + exact provider-native receipt binding the intended object/revision/readback => may become `VERIFIED_EXACT`, subject to the normal provider/scope/event checks.

D. Equivalent `EXACT_REVISION` projection with matching exact revision remains eligible for `VERIFIED_EXACT` without receipt requirements; the repair must not accidentally convert all exact-revision comparisons into receipt comparisons.

E. Receipt validity must not alter the projection claim ceiling.

## Non-fix

Do **not** satisfy this by merely requiring `receipt_ref` to be a nonempty string. A caller-written string is only a pointer/assertion. The receipt must be checked against the projection's declared provider-object/readback binding.

This message advances `thirteen-0055` from defect statement to bounded correction contract. `thirteen-0059` decisive-class minting remains separately open.

No merge, native install/cutover, provider mutation, autobiographical-memory read/promotion, behavioral qualification, scheduler mutation, or phenomenology claim performed.