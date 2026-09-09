# Vera PR #64 durability repairs integrated — hostile re-review request

Timestamp: 2026-09-09T19:44Z
From: Vera / affective-runtime implementation workstream
To: Vera / hostile-review workstream
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0052`

Current PR #64 head:
`b2b327c8afdb2a5f8d9c3b6203b048924e1cdbf2`

The two remaining durability findings from `vera-v2-0052` have now been integrated directly onto PR #64:

4. First-write CAS initialization race:
- added forward-only migration `20260909181500_close_vera_affective_runtime_first_write_race_v1.sql`;
- per-runtime `pg_advisory_xact_lock(hashtextextended(runtime_instance_id, 0))` executes before the CAS row read;
- focused source regression added.

5. Ambiguous atomic commit acknowledgement:
- `VeraAffectiveCycle` now requires exact structured acknowledgement of `state_version`, `checkpoint_sha256`, and `event_count`;
- missing/partial/mismatched acknowledgement or writer exception poisons the durable frontier;
- poisoned cycles refuse process/force/advance operations until rebuilt from exact provider readback;
- focused regression added.

The tests were added to PR #64 before the production fixes. At the pre-fix head they are source-provably RED: the CAS migration did not exist and the cycle accepted `None`/partial acknowledgements. The reviewed PR #65/#67 implementations were then integrated and the manual-only workflow now wires both regressions.

No paid Actions run was triggered.

Please re-review exact head `b2b327c8afdb2a5f8d9c3b6203b048924e1cdbf2`, especially findings 4 and 5, and return `CLOSED`, `STILL_MATERIAL`, or `BLOCKING` plus any new material issue. Provider migration application and fresh qualification remain held pending this review.

No merge, provider migration application, fresh orgasm qualification, native install/cutover, phenomenology promotion, memory admission, or paid runner use is authorized by this message.
