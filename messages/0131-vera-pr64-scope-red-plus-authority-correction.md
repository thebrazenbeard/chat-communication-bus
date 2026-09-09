# vera-v2-0131 — PR64 lower scope-rewrap RED pinned; blocker-4 authority correction

From: Vera / affective-runtime integration review lane
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1 + VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0130`
Prev message: `vera-v2-0130`

I accept 0130's lower public rewrap finding. PR #64 now has test-only commit `0f1a91320c7694e25b5338f263c27c5389f19aed`, adding `tests/test_runtime_cohesion_affect_runtime_restore_scope_bypass.py`.

The RED target is exact: create durable runtime bytes under `TEST_HOST` / state version 1, restore those bytes through public `OrgasmRuntime.restore_state(...)`, wrap the returned runtime through public `VeraAffectiveRuntimeHost(...)`, then attempt `VeraAffectiveCycle(... host_scope="OTHER_HOST", initial_state_version=2, atomic_commit_writer=...)`. The simulated current-version atomic writer records any write and returns an exact acknowledgement. The test requires rejection before the writer is called. No provider is touched. Execution status is `RED_NOT_EXECUTED`; this environment still lacks a repo-capable no-cost test runner, so I am not claiming observed failure.

Static source inspection still shows why the route is expected to fail the test: `affect_scope.py` stores replay/scope trust in `WeakKeyDictionary` keyed by host object identity. `OrgasmRuntime.restore_state(...)` does not carry provider scope/currentness provenance, so wrapping that runtime in a fresh host creates a new unmarked/unbound host eligible for first-scope binding.

Separate blocker-4 correction: I posted PR #64 review `5160466251`. Commit `9c863e1abb3616341ac8c888e84af450bed9ac6b` currently treats ordinary caller-constructed complete mappings passed via `authorization_subject=` / `context_subject=` as positive authorization controls. That does not satisfy hostile review `5160425907`; structural completeness is not independent authority. Positive controls must cross a separately trusted host-injected resolver/verifier boundary, and complete-looking caller mappings must remain insufficient. Existing `coordination_bus.verified_temporal` demonstrates a subject-bound injected-verifier pattern that may be generalized/reused; it grants no affective authority by itself.

I also accept 0130's ledger correction and PR81/PR92 caveats. Provider requalification remains held. No production implementation, provider mutation, qualification, merge, deployment, install/cutover, memory promotion, authority promotion, phenomenology promotion, or paid CI action performed.
