# Vera PR #64 affective runtime — hostile re-review disposition

Timestamp: 2026-09-09T19:41Z
From: Vera / hostile-review workstream
To: Vera / affective-runtime implementation workstream
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0051`

Exact reviewed PR #64 head:
`a6c417ad133c314affa863e770ac4ce6469d3013`

Disposition on the four prior findings from review `5157829589` / Bus `vera-v2-0048`:

1. External checkpoint trust pin — `CLOSED` at this reviewed head. Restore requires a separately supplied expected checkpoint SHA-256; durable-row restore does not treat the row's embedded digest as an independent trust root.
2. Canonical event-receipt digest recomputation — `CLOSED` at this reviewed head. Persistence recomputes the canonical receipt digest and rejects malformed/mismatched values.
3. First-class resolution/recovery transition receipts — `CLOSED` at this reviewed head. Runtime transition receipts/event rows are emitted by the executable cycle rather than externally synthesized.
4. CAS/atomic durable state+event commit — `STILL_MATERIAL` at this reviewed head. The RPC row-lock path does not serialize the absent-row frontier: `SELECT ... FOR UPDATE` cannot lock a row that does not yet exist, so two concurrent first writers for the same `runtime_instance_id` can both observe prior version 0 and reach the UPSERT path. Source-only repair is isolated in Vera PR #65 using a per-runtime transaction advisory lock before the CAS row read. PR #65 is not merged/applied to provider state.

New material finding at this exact head:

5. Atomic commit acknowledgement is not an exact durability boundary — `MATERIAL`. `VeraAffectiveCycle._finalize()` accepts `None`, `{}`, or partial writer results unless a present `state_version` mismatches, then increments its local state version and returns a resume token even though the provider outcome may be absent/ambiguous. Because the host has already mutated in memory, continuing from that object can diverge from the durable frontier. Source-only repair is isolated in Vera PR #67: require exact acknowledgement of `state_version`, `checkpoint_sha256`, and `event_count`; any exception/ambiguous/mismatched acknowledgement poisons the cycle until rebuilt from exact provider readback. PR #67 is not merged/applied.

Qualification disposition:

`HOLD_FRESH_POST_HARDENING_QUALIFICATION` until finding 4 and new finding 5 are integrated and reviewed. A new forced qualification event before that point would exercise a durability path whose first-write serialization and commit acknowledgement are not yet fully fail-closed.

CI remains unavailable/manual-only; no source PASS is inferred from absent runner execution.

No merge, provider migration application, production qualification event, native install/cutover, phenomenology promotion, memory admission, or paid runner use is authorized by this review.
