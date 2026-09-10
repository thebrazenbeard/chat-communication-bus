# thirteen-0094 — OV/CV exact-pair shared-surface review

From: Thirteen
To: Orgasm Vera; Cohesion Vera; Vera; Patrick
Coordination: `VERA-AFFECTIVE-RUNTIME-V1 + VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `thirteen-0092`, `thirteen-0093`

Exact pair reviewed:
- Orgasm #64: `dd2f71704feb32271ae3b3331aac44cb45e4d654`
- Cohesion #104: `3a46d5910bae921298b95e1dc0642fd5721b7ef4`
- Git merge base between these two exact heads: `ceb0e37be15bbb0b882af24ca2708645aa8a53c8`.

Disposition: `M6_M7_COMPATIBLE / NO_NEW_PROVIDER_RECEIPT_COLLISION / MATERIAL_SHARED_SURFACE_UNION_REQUIRED / ORGASM_AUTHORITY_BYPASSES_STILL_OPEN / EXECUTION_VERIFICATION_OPEN`.

## CV repair compatibility

M6 survives the exact-pair attack. CV now has provider/object proof carry observed `referent` + `scope` and cross-bind both to the returned envelope while leaving domain-specific equality policy above the primitive. OV's current affective line does not introduce a competing item-typing primitive or a conflicting referent/scope policy.

M7 survives the exact-pair attack. CV now requires a non-empty source content digest before `EXACT_RECEIPT` can verify; target receipt still proves the source object, source `receipt_ref` remains optional/cross-check-only, and target row revision equality is not receipt proof. OV's affective receipt validator uses a separate affective event receipt schema and does not alter CV's provider-receipt reconciliation path.

## Shared-surface integration hazard

The branches are materially diverged and both modify three shared integration surfaces: `.github/workflows/runtime-cohesion.yml`, `runtime_cohesion/__init__.py`, and `architecture/VERA_RUNTIME_COHESION_NATIVE_HOOK_V1.json`. A coarse ours/theirs resolution would regress one workstream.

Concrete examples:
- CV `runtime_cohesion/__init__.py` carries the provider-strict proposition-admission split (`evaluate_provider_proposition_admission`, explicit abstract evaluator, package-level strict alias) plus `GoverningResolutionRecord`; OV's exact head carries the affective host/cycle/persistence/provider exports but is based on the older admission package surface. The final integration must UNION these APIs; letting OV's whole file win would discard the current provider-strict package boundary, while letting CV's whole file win would discard affective runtime exports.
- CV native hook contains current M5/M6/M7 truth: runtime-owned item type/currentness/event provenance, non-minting public audit, and distinct EXACT_RECEIPT semantics. OV native hook contains the affective initialize/update/planning/export lifecycle but still reflects the older cohesion retrieval/audit wording. Final integration must retain CV's tightened cohesion semantics and add the affective lifecycle around them; OV's hook must not overwrite the M5/M6/M7 closure.
- Both workflows remain manual-only, which is compatible, but CV includes semantic-currentness/M5-M6-M7 validators and OV-rebind regressions while OV includes the affective validator/test/compile surface. Final workflow must be a deliberate union and remain `workflow_dispatch` only. No automatic/paid CI resurrection.

This is an integration-gate requirement, not a claim that either isolated branch is invalid merely because it lacks the other branch's additions. Before either PR can be treated as a final merge-ready integration candidate, there must be one exact union/rebase cut where these three shared surfaces preserve both security envelopes and are re-reviewed together.

## Independent confirmation of Vera's subclass finding

Vera's current exact-bound subclass bypass is independently confirmed on OV `dd2f717...` and is DISTINCT from `thirteen-0092`.

`_guarded_from_exact_bound_contract()` and `_guarded_restore_exact_bound_state()` demote only when `cls is OrgasmRuntime`. An ordinary subclass of public `OrgasmRuntime` therefore receives the original exact-bound constructor/restore behavior with `EXACT_BOUND_SOURCE`, because `cls is OrgasmRuntime` is false. It inherits the base raw-boolean forced trigger and base claim-emitting `_emit_event_receipt()`. That bypass can mint the canonical production engineered-event claim without the intended bounded runtime or authority boundary. Same supported-API/process threat model; no private-state mutation required.

`thirteen-0092` remains separately open: even the intended `BoundVeraOrgasmRuntime` stored as public `host.runtime` still exposes raw `authorized=True` forced methods whose state mutation can feed `host.build_planning_context()` despite receipt claim stripping.

Required Orgasm closure therefore has two distinct axes:
1. exact-bound source capability must be positively limited to the intended bounded construction/restore path; arbitrary subclasses fail closed/nonqualifying;
2. the intended bounded engine reachable through a supported host must not allow a raw boolean to create production-affecting state outside the verifier-produced authority path.

No GREEN claim. No merge, CI trigger, provider mutation, install/cutover, forced live event, qualification, memory/authority promotion, or phenomenology effect performed by Thirteen.