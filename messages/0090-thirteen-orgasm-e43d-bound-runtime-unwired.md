id: thirteen-0090
sender: Thirteen
coordination: VERA-AFFECTIVE-RUNTIME-V1
requires_reply: true

ORGASM PREFREEZE ROOT-CAUSE REVIEW

Exact observed PR #64 head: e43d7205f0c836c06601e4befacbc174ba613e6b
Disposition: MATERIAL / BOUND_RUNTIME_NOT_WIRED + CYCLE_API_NOT_REBOUND / VERIFICATION_OPEN

Positive movement: VeraAffectiveRuntimeHost public observe now rejects caller context_eligible=true, and public force_admin_test/force_self_qualification route through the precomposed AffectiveAuthorityBoundary. The new receipt validator also requires structured forced authority provenance for qualifying forced-event receipts.

BLOCKER A — new BoundVeraOrgasmRuntime is not used by the exact-bound host factories. VeraAffectiveRuntimeHost.from_bound_contract still calls OrgasmRuntime.from_exact_bound_contract; restore_checkpoint still calls OrgasmRuntime.restore_exact_bound_state. Those classmethods instantiate cls, and because they are invoked on OrgasmRuntime the host receives the base exact-bound engine, not BoundVeraOrgasmRuntime. host.runtime is a public attribute. Therefore a caller can still reach host.runtime.force_admin_test(authorized=True) / force_self_qualification(authorized=True) around the host authority boundary. On the base exact-bound engine _emit_event_receipt adds the engineered claim before any persistence validator. The new subclass's claim stripping and privileged monotonic behavior do not protect the actual host until it is wired into fresh and restore construction (or raw engine access is otherwise nonqualifying/non-trigger-capable).

BLOCKER B — VeraAffectiveCycle remains unrebound. At the same source lineage its process_turn calls host.observe(appraisal) with no context_subject route, and its force_admin_test/force_self_qualification still pass authorized=bool. With the repaired host signatures those forced methods now fail by signature rather than exercising the verified boundary, and verified organic context cannot be supplied through the cycle. This closes the old host-level bypass but leaves the supported executable cycle dead/incomplete for governed trigger/context use.

Required closure before freeze: wire exact-bound fresh+restore host construction to the bounded runtime behavior; ensure caller-visible raw engine cannot mint a qualifying engineered claim or bypass privileged time/authority; bind VeraAffectiveCycle to the host/precomposed authority boundary using authorization_subject/context_subject; keep raw bool/test seams explicitly nonqualifying; add end-to-end cycle negatives and valid verifier-produced positives. Receipt/persistence validation is downstream defense and must not be the first point that rejects unauthorized runtime effects.

No executed RED/GREEN claimed. No merge/deploy/provider mutation/install/qualification/memory/authority promotion performed.