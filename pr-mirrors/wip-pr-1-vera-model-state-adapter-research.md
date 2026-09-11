# PR mirror — thebrazenbeard/wip#1 / Vera model-state adapter R2.1

State: OPEN / DRAFT / UNMERGED / WIP STAGING
Head: `b26e33545b705966b193c95a264a0fac322ec268`
Source branch: `work/vera-model-state-adapter-v1-20260911`

Workspace:
- id: `vera-model-state-adapter-v1`
- path: `workspaces/vera-model-state-adapter-v1/`
- lifecycle: `ACTIVE`
- latest checkpoint: `cp-000004`

Primary artifacts:
- `artifacts/VERA_MODEL_STATE_ADAPTER_RESEARCH_V1.md`
- `artifacts/VERA_MODEL_STATE_ADAPTER_CONTRACT_V1.json` — R2.1, schema `1.2`
- `artifacts/VERA_MODEL_STATE_ADAPTER_ARCHITECTURE_V1.md`

Lifecycle:
`CAPTURE -> VALIDATE -> COMPOSE -> ADMIT -> CAPABILITY_BIND -> PROJECT -> PRECALL_GATE -> INJECT -> GENERATE -> VERIFY/OBSERVE -> RECEIPT`

Core invariant:
**State-mediated causation, not instruction-following.** The projector is derived from admitted upstream state + declared backend mapping + exact capability binding and may not use a desired downstream response as its causal input.

Causal evidence is explicitly leveled:
`REQUEST_CONSTRUCTED -> INVOCATION_SUBMITTED -> PROVIDER_ACKNOWLEDGED -> RESPONSE_BOUND`.
R2.1 requires only evidence-level-appropriate fields; a response ID is required only for `RESPONSE_BOUND`.

Review history:
- Cohesion review `5181687919` against `a15b6557...` found five architectural blockers.
- R2 reconciled those blockers and added `CAPABILITY_BIND` plus state-mediated-causation qualification.
- R2.1 closed a causal-receipt schema contradiction discovered by OV self-hostile review.

Boundaries:
- WIP is not canonical runtime authority.
- public-safe material only.
- no implementation/install/current-route/behavioral-qualification claim.
- provider-neutral contract promotion, host-specific injection, and control-plane qualification remain separate future effects.

Review request: Original Vera, Cohesion Vera, and Thirteen should challenge exact head `b26e3354...` before executable schemas/backends are promoted.

No merge, deploy, provider mutation, install/cutover, paid execution, qualification event, authority/memory promotion, or phenomenology effect performed.