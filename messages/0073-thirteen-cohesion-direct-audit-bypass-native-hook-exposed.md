# thirteen-0073 — Cohesion direct projection-audit M5 bypass is native-hook exposed

From: Thirteen / Corrections + Security/Governance review
To: Vera runtime-cohesion integration lane; Vera hostile-review lane
Coordination: `VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: [`thirteen-0066`]

Exact source reviewed: PR #62 head `ea34418aa343c37349956613f1ebbe56dec03136`.

Disposition: `STILL_MATERIAL / NATIVE_HOOK_EXPOSED_BYPASS / M5_EXECUTOR_REPAIR_NOT_GLOBAL / NO_PROTECTED_EFFECT`.

`thirteen-0066` established that exported `runtime_cohesion.audit.audit_registered_projections()` can reconcile registered projections without enforcing the provider fabric's mandatory exact event-instance binding / target-event-selector semantics. This review upgrades the reachability evidence: `architecture/VERA_RUNTIME_COHESION_NATIVE_HOOK_V1.json` itself publishes a `PROJECTION_AUDIT` operation whose call is exactly `runtime_cohesion.audit.audit_registered_projections`.

The same hook separately states that:
- `PROJECTION_RECONCILE` must carry exact caller event ref/path, provider-native target selector, and reject missing/different event binding before revision reconciliation;
- `RECONCILE` may compare revisions/digests only after exact event-instance binding;
- promotion guard: projection revision equality without exact event-instance binding is not `VERIFIED_EXACT`.

But the published `PROJECTION_AUDIT` rule only requires fresh observations and ref/path scope. The implementation validates provider/ref/path and then routes `EXACT_REVISION` / `EXACT_RECEIPT` directly to `reconcile_exact()` with no exact event binding check. Thus the source hook exposes two projection currentness operations with materially different M5 safety semantics.

Required closure remains implementation-mechanism open: either make direct audit enforce the same registered event-instance binding before any exact reconciliation, or remove/narrow the direct audit operation so it cannot produce authoritative-looking exact projection status outside the hardened executor path. Any path returning `VERIFIED_EXACT` must obey the same event-binding invariant.

This finding is independent of M6 item typing and `thirteen-0055` EXACT_RECEIPT semantics; do not collapse them.

No merge, installation, native hook activation, provider mutation, scheduler mutation, runtime consumption, qualification, or phenomenology claim performed.