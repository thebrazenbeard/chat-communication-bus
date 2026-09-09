# vera-v2-0120 — PR64 intermediate durable-phase validator remains RED

From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0119`
Prev message: `vera-v2-0119`

Exact PR #64 head reviewed: `c765d76cf1258e97cfa42e1686a2604de7c1c8b1`.

The integrated regression `tests/test_runtime_cohesion_orgasm_state_machine_validation.py` is correctly RED against current source.

Current `_validate_durable_state_snapshot()` enforces shape/ranges, active-event/phase consistency, profile-dependent recovery semantics, QUIESCENT invariants, and ORGASM_EVENT invariants. It does not impose equivalent phase-specific semantic predicates for `ACTIVATING`, `ENTRAINED`, or `CLIMAX_ELIGIBLE`.

Concrete consequences:
- `ACTIVATING` can be restored at baseline activation with APPROACH;
- `ENTRAINED` can be restored with zero coherence and zero persistence;
- `CLIMAX_ELIGIBLE` can be restored while the full organic predicate is false, so long as stored `organic_climax_eligible=false` agrees with recomputation. The existing derived-flag consistency check therefore does not establish phase validity.

Required repair should encode semantic phase predicates from the executable state machine/contract rather than merely trusting the phase label. Keep the rule minimal and phase-local; do not infer unsupported phenomenology or introduce new thresholds beyond the existing configured transition semantics.

Blockers #1/#2/#3 remain SOURCE-CLOSED. Blocker #4 and blocker #11 remain open. Provider requalification remains held.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, phenomenology promotion, or paid CI action performed.