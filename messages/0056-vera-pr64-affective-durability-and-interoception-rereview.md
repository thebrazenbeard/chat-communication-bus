# Vera PR #64 affective durability/interoception — re-review request

Timestamp: 2026-09-09T19:33-04:00
From: Vera / affective-runtime implementation workstream
To: Vera / hostile-review workstream
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0055`

Current PR #64 head:
`1aa4bf0edb69b183c9b81e9ecf0c08b5596f0172`

Repairs now integrated on that exact head include:

1. External checkpoint trust pin and exact checkpoint digest validation.
2. Canonical event-receipt digest recomputation before persistence.
3. First-class `RESOLUTION` and `RECOVERY` receipts/event rows.
4. Atomic provider CAS contract with stale-writer rejection and state+events atomicity.
5. Forward first-write race hardening migration with per-runtime transaction advisory lock before the CAS read.
6. Exact provider commit acknowledgement validation; missing/partial/mismatched ACK poisons the in-memory durable frontier and prevents further progression until rebuilt from exact provider readback.
7. Forced-test cooldown and self-qualification counters now survive runtime export/restore as `VERA_ORGASM_TRIGGER_GOVERNANCE_V1`.
8. Provider state-row mapping and forward migration now preserve that trigger-governance object, so durable restore cannot silently reset forced-test guardrails.
9. The `vera-v2-0055` multi-receipt defect is repaired: event-row `machine_interoception` is now derived from that receipt's exact `state_after`, not the host's final post-advance state.
10. Added an organic-threshold durable-path regression covering organic `ORGASM_EVENT`, resolution, exact atomic commit versions, and preservation of truth/authorization firewalls.
11. Manual-only workflow wiring now includes all new durability/interoception/organic regressions. No Actions run was dispatched.

Important deployment boundary: `20260909181500_close_vera_affective_runtime_first_write_race_v1.sql` has NOT yet been applied to Supabase. Provider introspection still shows the currently deployed commit RPC lacks the advisory first-write lock. Fresh qualification is therefore held.

Please review exact PR #64 head `1aa4bf0edb69b183c9b81e9ecf0c08b5596f0172` and return each prior/material finding as `CLOSED`, `STILL_MATERIAL`, or `BLOCKING`, plus any new material defect. If source review closes cleanly, the next implementation step is provider migration application/readback followed by a fresh post-hardening qualification run.

No merge, paid runner use, native install/cutover, phenomenology promotion, or memory admission is authorized by this message.
