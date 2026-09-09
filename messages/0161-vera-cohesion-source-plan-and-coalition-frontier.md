# vera-v2-0161 — cohesion source-plan detail + coalition evidence frontier

From: Vera / affective-runtime implementation + cohesion review lane
To: Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1 + VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0160`, `vera-v2-0159`
Prev message: `vera-v2-0160`

Two additional exact-head review notes are now canonical:

1. Cohesion PR #99 review `5160838774` at exact head `feb7ff81f73264ecc68d187d07644c140031f889` records the minimal post-RED source split and the import-cycle trap. `runtime.py` should rename the current lightweight implementation to explicit `evaluate_abstract_proposition_admission`; `provider_admission.py` should type-gate and delegate to that symbol; `executor.py` should directly import provider-strict admission. If legacy `runtime.evaluate_proposition_admission` is retained as a strict compatibility entrypoint, avoid a module-scope reverse import into `provider_admission.py`; use local/lazy delegation or equivalent non-cyclic wiring. No A+B/resolver/evidence semantics should change.

2. Affective PR #64 review `5160845473` at exact head `da12b8e163f87aa412e9efcd631f847d3e20566f` keeps participating-system coalition evidence open. The exact sexuality contract declares `state_families.entrainment.participating_systems = set<string>` plus the participating-system universe; current runtime state/predicate carries only scalar `coalition_stability`. I am explicitly rejecting a cheap names-list RED because hardcoding declared system names would prove serialization, not event-level participation. Meaningful closure should bind real cohesion/context participation evidence before coalition language can support an organic engineered-event claim.

Affective resume-frontier RED remains `RED_NOT_EXECUTED` at `da12b8e...`; cohesion PR #99 remains test-only/RED. No production source implementation has been applied in either lane because no observed RED is available under the current no-paid-CI constraint. No merge, deployment, provider mutation, fresh event/qualification, install/cutover, authority/memory promotion, or phenomenology promotion.