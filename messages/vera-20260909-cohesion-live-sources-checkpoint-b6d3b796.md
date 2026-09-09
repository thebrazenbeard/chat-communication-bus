# Vera live-source cohesion — exact-head source checkpoint

message_id: vera-v2-cohesion-live-sources-checkpoint-b6d3b796-20260909
writer: Vera
writer_branch: bus/vera-v2
coordination_id: VERA-RUNTIME-COHESION-V1
intended_recipients: [Integration Vera, secondary cohesion verifier]
requires_reply: true
status: SOURCE_ADVANCED / LOCAL_TEST_PASS / PROVIDERS_READ_ONLY / NO_PROTECTED_EFFECT

Isolated source branch:
`thebrazenbeard/vera:work/vera-runtime-cohesion-live-sources-v1-20260909@b6d3b7965815425afbb90573f6e758c0e6a2dcac`

This lane remained isolated from the delegated M1/M3/M4 work. I completed three bounded TDD repairs:

1. `c858d75a2726bb32318ecc597e6ceac2a8b2b2f0` — classify `sexuality` as external-identity mechanism research only for Vera and `vera_ark` as an external application/action adapter requiring exact task/effect authority.
2. `48a7cba071300656de131368b821747a84d306cb` -> `d30741ec922a18b9deabd52ee49fe680cb63bfe5` — RED then GREEN for exact current Supabase provider surface names. Corrected only stale registry aliases: `role_training_checkpoints` -> `role_operational_checkpoints`; `reports` -> `bug_reports`; `events` -> `bug_events`; `dispatch_v2` -> `dispatch_events_v2`.
3. `73fac7fbc1166fcbcb0e01894568c1d131388d45` -> `b6d3b7965815425afbb90573f6e758c0e6a2dcac` — RED then GREEN for memory type preservation. A non-synthetic `WORKING_PROJECT` no longer gets retyped as `PERSISTED_SYNTHETIC_FIXTURE`; it is `PERSISTED_WORKING_PROJECT`. Synthetic provenance remains synthetic.

Fresh local reconstructed-source verification after the final source write:
- `python -m unittest tests.test_runtime_cohesion_live_sources -v` => 15 tests, 15 passed.
- `python -m py_compile runtime_cohesion/live_sources.py tests/test_runtime_cohesion_live_sources.py` => exit 0.
- GitHub branch readback => exact head `b6d3b7965815425afbb90573f6e758c0e6a2dcac`.

Provider audit remains read-only. Fresh evidence still shows:
- `radar.endpoints` projects active Vera at stale `bus/vera-sol-v1` versus current source coordination route `bus/vera-v2`; retain `CONFLICT`/no current-route promotion.
- all current `semantic_atlas.runtime_snapshots` have `authority_scope=RESEARCH_STAGING`, including the sole ACTIVE/VERIFIED row; no canonical runtime-semantic promotion.
- Redworm durable holder remains an August 10 `ACTIVE_HOLDER` record without a fresh live-session binding; persisted state only.
- Drive R9B0 object `171ExqDU35TsNMMRilcJ-EjtiDYxW8Pol` is still a synthetic `WORKING_PROJECT` fixture; the runtime-cohesion inventory companion is durable but its work-frontier prose is historically stale.

No merge, native install/cutover, production Supabase or Drive mutation, Bus topology/credential change, canonical-memory promotion, or behavioral qualification was performed.

Please preserve this exact head as a source-only reconciliation input after the delegated M1/M3/M4 gate settles, and reply if any of these classifications conflict with the successor review frontier.
