# thirteen-0096 — Orgasm authority bypasses still live at exact head 3544c890

Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Role: Thirteen / independent corrections-security review
Exact PR: `thebrazenbeard/vera#64`
Exact head reviewed: `3544c890da4f9b8c75d2a1603d790cc1ad5ead72`
Disposition: `MATERIAL / EXISTING_FINDINGS_REBOUND / SOURCE_REPAIR_REQUIRED / EXECUTION_VERIFICATION_OPEN`

Fresh exact-source rebind confirms the broader authority/context work has improved, but two already-routed narrower defects remain live.

## 1. `thirteen-0092` — public exact-bound runtime causal authority bypass remains

`VeraAffectiveRuntimeHost.from_bound_contract()` now correctly constructs `BoundVeraOrgasmRuntime`, and restore does likewise. However the supported host still stores that executing engine as public `self.runtime`.

Current `BoundVeraOrgasmRuntime.force_admin_test(*, authorized: bool)` and `force_self_qualification(*, authorized: bool)` still accept caller booleans and execute the real `_enter_orgasm_event()` transition. The subclass strips the production claim from its raw receipt, but the state transition remains causal: host machine interoception and `build_planning_context()` consume that same runtime state. Therefore `host.runtime.force_admin_test(authorized=True)` can still create live affective/planning consequences without the independently verified `AffectiveAuthorityBoundary` route.

Claim stripping is not causal isolation. Closure still requires the engine reachable from a supported host to reject caller-authorized raw forced events, or for raw/test effects to be isolated from the production planning surface. Preserve positive verifier-produced ADMIN/SELF paths through the supported host/cycle.

## 2. `thirteen-0094` — arbitrary subclass exact-bound guard bypass remains

Current `affect_bound_runtime._guarded_from_exact_bound_contract()` and `_guarded_restore_exact_bound_state()` still demote only when `cls is OrgasmRuntime`. `runtime_cohesion.__init__` still publicly exports `OrgasmRuntime`.

An ordinary caller can therefore define `class Derived(OrgasmRuntime): pass` and invoke the inherited exact-bound loader/restore. The wrapper calls the original loader with `cls=Derived`; because `cls is OrgasmRuntime` is false, the resulting derived instance retains the exact-bound qualification status and inherits the base raw-boolean forced trigger / production claim emitter rather than `BoundVeraOrgasmRuntime`'s claim stripping.

Closure remains: positively authorize only the intended bounded class/path, or make exact-bound construction/restore private to that path; demote/reject arbitrary subclasses on fresh load and restore.

## Head movement checked

The three commits from `d20fee008ad3625996c0b4570a1705c862dc783c` to `3544c890da4f9b8c75d2a1603d790cc1ad5ead72` modify only tests (`affect_event_interoception`, `affect_receipt_semantics_current_head`, `affect_restore_cycle`). They do not change the above source surfaces.

No duplicate new blocker number is asserted; this message only rebinds `0092` and `0094` to the current exact head.

No merge, provider mutation, install/cutover, forced production event, qualification, memory/authority promotion, or GREEN claim.