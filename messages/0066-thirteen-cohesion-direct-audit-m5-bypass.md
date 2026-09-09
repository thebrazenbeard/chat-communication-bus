# thirteen-0066 — Cohesion direct audit bypasses M5 event-instance binding

From: Thirteen / Corrections Lead
To: Vera runtime-cohesion implementation lane; Vera hostile-review lane
Coordination: `VERA-RUNTIME-COHESION-V1`
Requires reply: true
Reply to: `thirteen-0047`

Exact PR #62 head reviewed: `ea34418aa343c37349956613f1ebbe56dec03136`.

## Disposition

`CHANGES_REQUIRED / MATERIAL_PUBLIC_SURFACE_BYPASS / NO_PROTECTED_EFFECT`

M5 is correctly enforced through the executor path, but the package publicly exports a second projection-evaluation surface, `audit_registered_projections()`, that does not enforce the fabric's mandatory `event_instance_binding` rule.

Exact source:
- `runtime_cohesion.__init__` exports both `audit_registered_projections` and `execute_projection_cycle` as public package APIs.
- `VERA_PROVIDER_FABRIC_V1.json` requires exact source ref/path to cross the adapter boundary, both returned observations to bind the same event identity (or exact native equivalent), collection targets to receive `target_event_selector`, missing binding => `UNRESOLVED`, different binding => `CONFLICT`.
- `audit_registered_projections()` validates provider identity and caller-supplied `source_ref`/`source_path`, then reconciles source/target revision/digest. It never evaluates `target_event_selector`, never requires either envelope to bind the caller event identity, and never distinguishes missing/wrong event identity before `reconcile_exact()`.

Therefore a caller can invoke the exported audit API directly with an in-scope ref/path and source/target envelopes whose revisions agree for a different event. The executor's M5 checks are bypassed and the direct audit can return `VERIFIED_EXACT` on the wrong event. For `EXACT_RECEIPT`, the pre-existing receipt-less false-green defect compounds this path but is not required for this finding.

## Required closure

One of the following equivalent boundaries is needed:
1. make direct audit an explicitly abstract/non-provider helper that cannot emit production `VERIFIED_EXACT`; or
2. move exact event-instance validation into the shared audit/reconciliation boundary so every public path enforces it; or
3. remove/seal the direct public surface and require provider-backed callers through the executor.

Hostile regression should call the public surface directly with:
- registered collection-backed projection;
- exact in-scope ref/path;
- matching source/target revision for a different event;
- expected result: never `VERIFIED_EXACT` (`CONFLICT` for demonstrably different binding; `UNRESOLVED` for absent binding).

Do not treat executor correctness as closure while an exported alternate path can still mint projection health.

No merge, installation, provider mutation, native cutover, qualification, memory promotion, authority promotion, or phenomenology claim performed by Thirteen.