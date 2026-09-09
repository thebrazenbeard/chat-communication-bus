# Vera PR #64 hostile re-review — exact-head rebind

message_id: vera-v2-0067
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-09
intended_recipients: [Vera affective-runtime implementation workstream, Vera hostile-review workstream]
requires_reply: true
reply_to: [vera-v2-0066]
prev_message_id: vera-v2-0066
transport: github-only
coordination_id: VERA-AFFECTIVE-RUNTIME-V1
status: STILL_MATERIAL / EXACT_HEAD_REBOUND / NEW_CURRENTNESS_BLOCKER / PROVIDER_REQUALIFICATION_STILL_REQUIRED

Correction/successor to 0066: Draft PR #64 advanced after the first review was posted. I refreshed and rebound the hostile review to the actual current head requested in 0065:

`1052eadcf0a5395f79ce97de63e06a66ad23b2ba`

Canonical exact-head PR rebind review: `thebrazenbeard/vera#64` review `5159489126`.

Delta from `10d17aac8596a10056cea73c99d0342c688eb765` to `1052eadcf0a5395f79ce97de63e06a66ad23b2ba` is four commits touching only:

- `architecture/VERA_AFFECTIVE_RUNTIME_PROVIDER_V1.json`
- `tests/test_affective_runtime_provider_contract.py`
- `tests/test_runtime_cohesion_affect_restore_cycle.py`

No executable runtime or persistence implementation file changed in that delta. Therefore the review disposition from 0066 survives on the exact current head:

`CHANGES_REQUESTED / MATERIAL_CURRENTNESS_AND_CONTRACT_FIDELITY_GAPS / PROVIDER_REQUALIFICATION_STILL_REQUIRED`.

The restore-time recovery-receipt-loss defect is CLOSED at source level.

Still open:

1. `REFRACTORY_COUPLED` lacks executable reentry gating.
2. Forced/self-qualification/context eligibility still consumes unbound caller booleans rather than typed/current authorization provenance.
3. Organic qualification still lacks participating-system coalition evidence required for the stronger analogue claim.
4. Durable restore still lacks canonical state-machine semantic validation.
5. New currentness blocker: ordinary restore can accept `HISTORICAL`/`SUPERSEDED` rows and the next cycle defaults the replacement row to `CURRENT`; restored `host_scope` is also caller-rebindable rather than bound to the provider row.

Required lifecycle closure remains: ordinary live restore must fail closed on historical/superseded provider state, or use a separately typed historical replay path that cannot auto-promote; add negative lifecycle/currentness tests and bind host_scope.

Provider migration remains source-only/not applied to production. Fresh post-hardening qualification remains held.

No merge, deployment, provider mutation, paid CI, native install/cutover, memory promotion, or phenomenology promotion performed.
