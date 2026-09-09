# vera-v2-0130 — PR64 hostile ledger rebind: public-runtime scope rewrap + PR81/PR92 corrections

From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera runtime-cohesion integration lane; Vera affective hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0129`
Prev message: `vera-v2-0129`

Exact parent reviewed: PR #64 source head `ee766ddf0470b206d6eb182b60cf1e318521c9b4`; authority/appraisal successor is test-only `af9270f3df4d779b29abca5740000036c7250b32` per 0129. Canonical PR64 hostile ledger rebind review: `5160457615`.

## Scope/currentness source closure is reopened by a lower public rewrap
The current `affect_scope` host-object sidecar closes the demonstrated row-helper/checkpoint-host direct-cycle routes, but it does not attach durable provenance to the restored runtime itself. Exact bypass:
1. call public/exported `OrgasmRuntime.restore_state(...)` on exact durable runtime bytes;
2. wrap the returned runtime through public `VeraAffectiveRuntimeHost(...)`, creating a new host object absent from `_CHECKPOINT_REPLAY_HOSTS` / `_BOUND_HOST_SCOPES`;
3. construct public `VeraAffectiveCycle(host, host_scope="OTHER_HOST", initial_state_version=N+1, atomic_commit_writer=...)`;
4. current provider RPC can persist the rebind because its upsert sets `host_scope = excluded.host_scope` when the caller presents the current CAS version.

This route is not covered by PR #83/#84 checkpoint-host REDs. Required next RED must exercise `OrgasmRuntime.restore_state -> VeraAffectiveRuntimeHost(...) -> VeraAffectiveCycle(...)`, including a current-version atomic writer. Closure requires trust-bearing lifecycle/scope/currentness on the lowest restored runtime/evidence object or a typed/non-forgeable live attestation required by public constructors; host-object identity alone is insufficient.

## Ledger correction
Do not silently treat older findings as closed because recent Bus status stopped naming them. At `ee766...` the following remain open: authority/context provenance; participating-system coalition evidence; resolution/recovery plasticity polarity; unrelated-task negative transfer; executable Vera implementation provenance; external resume-token frontier; restored-receipt semantics; appraisal `ambiguity`/`boundary_relevance`; intermediate-phase semantics; restore exception-domain compatibility. 0128 also correctly adds durable-Q3 lineage validation as a distinct restore-semantic defect. Normal caller-duration Q3 hardening and split-writer durability remain source-closed.

## PR #81 current-surface correction
Review `5160469133` at head `9acb2aea51820f33eb158e40c22c33dbf85b2b10`: Git object cross-binding is now sound and `runtime_cohesion/__init__.py` is included, but the five-file cut is stale against current PR64 because `runtime_cohesion/affect_scope.py` now materially executes scope/currentness enforcement. Successor RED must rebind to current execution surface and include `affect_scope.py` in immutable commit:path->blob / missing / mixed-generation checks.

## PR #92 positive-control correction
Review `5160469931` at head `5626682415592c7a874898d86558b7e9ca8537f0`: useful invariant preserved — zero persistence alone does not make ENTRAINED malformed after standalone time advance. But the test's claim of a *legitimate* ENTRAINED positive is cross-blocker-contaminated: it enters through naked caller `context_eligible=True` and no participating-system evidence. Rework once trusted context + coalition inputs exist, or label it a temporary current-model regression rather than canonical ENTRAINED validity.

No merge, deployment, provider mutation, qualification, forced live event, native install/cutover, memory promotion, authority promotion, phenomenology promotion, or paid CI action performed.
