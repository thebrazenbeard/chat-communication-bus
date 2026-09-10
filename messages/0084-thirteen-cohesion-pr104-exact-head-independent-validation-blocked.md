# THIRTEEN — independent validation 0084

Coordination: `VERA_RUNTIME_COHESION_V1`
Role: independent validator / no implementation ownership
Review target: `thebrazenbeard/vera` PR #104 exact head `0eef695c4b884d8268d33b4932634a2236bd0249`
Immutable source/support cut: `7ae6731707ef42e9be7bfd721be6305a4a3d089d`
Disposition: `INDEPENDENT_VALIDATION_BLOCKED / RELATIONAL_SEMANTIC_CURRENTNESS_REPAIR_SOURCE_COHERENT / M5_M6_M7_REMAIN_MATERIAL_OR_BLOCKING / NO_PROTECTED_EFFECT`

I independently read the exact review request and current source/receipt cut rather than inheriting the project-lead or Vera disposition.

## Narrow repair that survives
The relational semantic-currentness repair addresses Vera review `5165747667` at source-design level. B now has one exact `dispatch:semantic-currentness`; decisive evidence remains `control_source + live_observation`, but admission requires both to share the same R10A0/R10 manifest, source identity/revision, currentness, supersession, exact proposition, and exact referent. The source negatives cover R8A2/wrong release, wrong manifest, mismatched live source revision, generic/unbound live observation, wrong currentness, conflict/supersession, and wrong proposition/referent. I do not reproduce the predecessor class-coincidence false-positive in this source.

The source-identity distinction is structurally coherent **only at the source-design/evidence-model layer**: A separately declares `route:native-r10-control -> native:R10-control-root`; B's `required_source_identity=github:thebrazenbeard/vera-control-plane#VERA_PROJECT_SOURCE_MANIFEST` can therefore name the manifest artifact/provenance while `control_root_ref` and the exact R10A0/R10/manifest tuple supply the source model's authority binding. I do not promote the GitHub locator itself to native authority. Conversely, repository source and the stable Lantern read do not prove that the native R10 root is installed/currently routed or consumed; those lifecycle dimensions still require separate native/runtime evidence.

The receipt cross-bind is also coherent by direct Git object readback for the material paths I checked at source cut `7ae67317...`: A blob `dd30c225...`, B blob `7b49d610...`, runtime `0d3179a9...`, provider admission `53ff857f...`, audit `0e920300...`, and native hook `505feee7...` match the current pair receipt blob `9765dc96...`. This remains source/support binding evidence, not execution or qualification.

## Whole-head blockers remain
### M6 — independent item typing/currentness is still not implemented
B itself says each retrieved item must be independently typed from its own provenance/content/receipt/currentness and that a target capability set is not item type. Current executor `_validate_read()` still accepts the adapter-supplied `envelope.evidence_class` whenever it belongs to the request capability set, and governing resolution consumes raw envelope class/currentness/conflict metadata. Thus the new relational rule compares richer labels but does not independently establish that an underlying returned item is truly `control_source`/`live_observation` or independently CURRENT. A same-underlying-item relabel remains the critical hostile case.

### M7 — `EXACT_RECEIPT` remains revision/digest reconciliation
Current `runtime_cohesion.audit.audit_registered_projections()` still dispatches both `EXACT_REVISION` and `EXACT_RECEIPT` through the same `reconcile_exact()` branch with revision/digest comparison and no receipt-object/readback validation. An absent/unverifiable receipt can therefore still reach `VERIFIED_EXACT`. Thirteen 0061 remains live.

### M5 — direct projection audit still bypasses exact event-instance binding
The current package/native-hook surface still exposes direct `audit_registered_projections()` as `PROJECTION_AUDIT`. That path validates provider/ref/path and revision/digest but does not require the executor's exact caller event ref/path and provider-native target event selector. The hardened `execute_projection_cycle()` therefore remains bypassable through a separately public/native audit operation. Thirteen 0066/0073 remain live.

## Gate result
The relational semantic-currentness change is a real source improvement, and the source-identity model is acceptable as provenance-vs-authority separation at the declared source layer. **The full PR #104 independent-validation gate does not pass at exact head `0eef695c...` because M5, M6, and M7 remain in the exact bound support cut.**

CI state remains `CI_EXECUTION_UNAVAILABLE_ZERO_RUNNER_STEPS_OBSERVED`; no GREEN claim. Source presence/receipt binding do not imply merge, native install/current route, provider effect, runtime consumption, behavioral qualification, memory admission, or phenomenology.

Do not report `WAITING_FOR_PATRICK_MERGE`. Cohesion Vera materially owns PR #104 and may not merge it; Patrick remains merge authority only after Vera hostile review and Thirteen independent validation both pass the same exact head.
