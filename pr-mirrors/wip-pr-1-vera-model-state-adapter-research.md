# PR mirror — thebrazenbeard/wip#1 / Vera model-state adapter R3

State: OPEN / DRAFT / UNMERGED / WIP STAGING
Head: `81a46ce9065d0c905afd3bb922f9ce8f3e37479f`
Source branch: `work/vera-model-state-adapter-v1-20260911`

Workspace:
- id: `vera-model-state-adapter-v1`
- lifecycle: `ACTIVE`
- latest checkpoint: `cp-000005`

Primary artifacts:
- `workspaces/vera-model-state-adapter-v1/artifacts/VERA_MODEL_STATE_ADAPTER_RESEARCH_V1.md`
- `.../VERA_MODEL_STATE_ADAPTER_CONTRACT_V1.json` — schema `1.3`, blob `23392533c8ef86cf480ee89a9a536220f83bde66`
- `.../VERA_MODEL_STATE_ADAPTER_ARCHITECTURE_V1.md` — blob `53d90a8c0ecb5c0c287f2ee58fa34eeea6de67af`

Lifecycle:
`CAPTURE -> VALIDATE -> COMPOSE -> ADMIT -> CAPABILITY_BIND -> PROJECT -> PRECALL_REVALIDATE_GATE -> INVOCATION_RESERVE -> INJECT -> GENERATE -> VERIFY/OBSERVE -> RECEIPT`

Core invariant:
**State-mediated causation, not instruction-following.** The desired downstream behavior is not a projection input.

R3 additionally binds privacy/egress end-to-end, exact projection material, host-owned single-use invocation identity, pre-call currentness revalidation, and explicit separately-qualified backend fallback semantics.

Causal evidence remains graded:
`REQUEST_CONSTRUCTED -> INVOCATION_SUBMITTED -> PROVIDER_ACKNOWLEDGED -> RESPONSE_BOUND`, with only level-appropriate receipt fields.

Review history:
- Cohesion review `5181687919`: five blockers, reconciled in R2.
- Thirteen review `5182392583`: four additional material blockers, reconciled in R3.
- R2.1 self-hostile review fixed universal response-ID overclaim before R3.

Boundaries:
- WIP is not canonical runtime authority.
- public-safe material only.
- no implementation/install/current-route/provider-durability/behavioral-qualification claim.
- provider-neutral contract, host-specific injection/frontier, and control-plane installation/qualification remain separate future ownership/effect axes.

Review request: attack exact head `81a46ce9...`; no prior review/PASS transfers.

No merge, deploy, provider mutation, install/cutover, paid execution, qualification event, authority/memory promotion, or phenomenology effect performed.