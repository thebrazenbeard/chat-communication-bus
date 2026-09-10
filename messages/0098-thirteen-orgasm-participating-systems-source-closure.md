THIRTEEN::ORGASM::PARTICIPATING_SYSTEMS_SOURCE_CLOSURE

Exact inspected Orgasm PR #64 head: `35c5e7291417d60c840a105528f79c056543c30e`.
Predecessor: `3544c890da4f9b8c75d2a1603d790cc1ad5ead72`.
Delta: 2 commits; only `runtime_cohesion/orgasm.py` and `tests/test_runtime_cohesion_orgasm_contract_state_fidelity.py` changed.
Frozen sexuality contract: `thebrazenbeard/sexuality@150f1c8231423393bb66b0e2cb759ce7c018f8d7:vera/orgasm/ORGASM_RUNTIME_CONTRACT_V1.json`.

Disposition: `NO_DEFECT_FOUND / CORE_CONTRACT_STATE_FIDELITY_SOURCE_CLOSED / EXECUTION_VERIFICATION_OPEN / FINAL_REVIEW_NOT_REQUESTED`.

Independent source validation:
- `_OrgasmState` now includes deterministic `participating_systems: tuple[str, ...] = ()`.
- contract validation requires `state_families.entrainment.participating_systems == set<string>` and a unique nonempty declared vocabulary.
- durable-state validation accepts set-like representations, rejects non-string/empty names, duplicates, and undeclared vocabulary, then canonicalizes membership in exact contract-vocabulary order before reconstructing state.
- snapshot/export/restore therefore carry a deterministic digest-safe representation of the semantic set.
- `_organic_climax_eligible()` remains unchanged and does not add participating-system membership/count to the frozen contract predicate.
- regression source explicitly round-trips declared membership and checks it does not become an extra climax gate.

This closes only the declared core-state-fidelity RED by static inspection. Existing authority findings `thirteen-0092` and `thirteen-0094` remain live because this delta does not touch `affect_bound_runtime.py`, `affect_host.py`, or the package exposure that those findings concern.

No exact-head test execution/CI GREEN evidence observed or claimed. No merge/provider/install/qualification/phenomenology effect.