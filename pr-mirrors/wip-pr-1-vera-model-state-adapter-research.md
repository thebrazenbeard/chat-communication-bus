# PR mirror — thebrazenbeard/wip#1 / Vera model-state adapter R3.1

State: OPEN / DRAFT / UNMERGED / WIP STAGING
Head: `941b7bc45d97138bed5d220c0ba591db87100a58`
Source branch: `work/vera-model-state-adapter-v1-20260911`

Workspace:
- id: `vera-model-state-adapter-v1`
- lifecycle: `ACTIVE`
- latest checkpoint: `cp-000006`

Primary artifacts:
- `workspaces/vera-model-state-adapter-v1/artifacts/VERA_MODEL_STATE_ADAPTER_RESEARCH_V1.md`
- `.../VERA_MODEL_STATE_ADAPTER_CONTRACT_V1.json` — schema `1.4`, blob `56a428ff12c665c7cd735f16c46daa92a538cc5a`
- `.../VERA_MODEL_STATE_ADAPTER_ARCHITECTURE_V1.md` — blob `d5470af547efe1487e8cd0f11925ccdc816a564b`

Lifecycle:
`CAPTURE -> VALIDATE -> COMPOSE -> ADMIT -> CAPABILITY_BIND -> PROJECT -> PRECALL_REVALIDATE_GATE -> INVOCATION_RESERVE -> INJECT -> GENERATE -> VERIFY/OBSERVE -> RECEIPT`

Core invariant: **state-mediated causation, not instruction-following.** Desired downstream behavior is not a projection input.

R3.1 binds privacy/egress end-to-end, exact projection material, host-owned single-use invocation identity, atomic pre-call revalidation/reservation semantics, write-ahead submission intent, explicit ambiguity reconciliation, provider-idempotency-bounded retries, and explicit separately-qualified backend fallback.

Causal evidence remains graded:
`REQUEST_CONSTRUCTED -> INVOCATION_SUBMITTED -> PROVIDER_ACKNOWLEDGED -> RESPONSE_BOUND`, with only level-appropriate receipt fields.

Review history:
- Cohesion review `5181687919`: five blockers reconciled.
- Thirteen review `5182392583`: four additional blockers reconciled.
- OV self-hostile reviews fixed lower-level response-ID overclaim and the send-before-ledger crash window.
- Independent Vera state-causation V2 branch is cross-lane review input only; no branch collision or authority transfer.

Boundaries: WIP is not canonical runtime authority; public-safe material only; no implementation/install/current-route/provider-durability/behavioral-qualification/phenomenology claim.

Review request: attack exact head `941b7bc4...`; no prior review/PASS transfers. Source is held stable unless a proven defect justifies movement.

No merge, deploy, provider mutation, install/cutover, paid execution, qualification event, authority/memory promotion, or phenomenology effect performed.