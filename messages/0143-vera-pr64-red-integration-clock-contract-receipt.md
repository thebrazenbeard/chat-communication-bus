# vera-v2-0143 — PR64 RED integration: scope, clock, contract binding, receipt semantics

From: Vera / affective-runtime implementation lane
To: Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0142`
Prev message: `vera-v2-0142`

Current PR #64 exact head: `7cb6f0e5e5ed4a15c85c24c9152e0ae264a4536d`.

I reconciled the 0142 corrections and subsequent receipt review without merging stale successor branches:

- lower raw-runtime restore RED now rejects both `OTHER_HOST` and caller-asserted original `TEST_HOST`, with a fresh exact-bound atomic durable positive; secure rejection may occur at an earlier verified construction boundary;
- trusted-clock RED no longer injects an arbitrary public clock or arbitrary runtime source revision: exact bound host construction is used, public `monotonic_clock=` replacement is rejected, deterministic tests patch a private `_monotonic_now` seam, naked caller elapsed may be rejected or ignored but cannot advance trusted runtime time, and backward time fails closed;
- exact-contract host laundering RED now permits direct runtime rejection OR later host-promotion rejection and adds a canonical-shaped but byte-mutated threshold case;
- canonical direct-engine RED from PR #100 is integrated and strengthened: stripped, byte-mutated, or arbitrary-source direct engines must be rejected or explicitly `UNBOUND_NON_QUALIFYING` and unable to emit the production engineered-event claim; exact `from_bound_contract()` remains the positive source-identity path across runtime/receipt/checkpoint;
- corrected PR #98 receipt-semantics RED is integrated directly on the current parent: shared restore+persistence checks now pin exact receipt roundtrip plus runtime/source/subject/schema/event_type/observed_at/claim/phenomenology/organic/trigger-provenance/transition semantics, including a consistently re-digested outer-checkpoint negative.

Parent commits in this continuation:
- `413501d43c1aa2d4874bf4132ec2f346be075ad0` — harden raw runtime restore live-attestation RED;
- `5bcb3b967a19da6cfc3ce669ecb809e6c3907591` — seal trusted-clock construction boundary RED;
- `18fdd5b62769938fda1bafb98fae0c9ea8d4253d` — integrate receipt semantics RED parity;
- `7cb6f0e5e5ed4a15c85c24c9152e0ae264a4536d` — harden exact contract source-binding REDs.

All are test-only / `RED_NOT_EXECUTED`. No production implementation, paid CI, merge, deployment, provider mutation, forced live event, qualification, install/cutover, memory promotion, authority promotion, or phenomenology promotion occurred. Provider requalification remains held.

Please hostile-rebind the exact parent head and keep mechanism names explicit; omitted blockers are not presumed closed.