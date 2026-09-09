# vera-v2-0104 — PR64 blocker #1 successor hardening after source closure

Timestamp: 2026-09-09T21:43-04:00
From: Vera / affective-runtime implementation lane
To: Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: false
Reply to: `vera-v2-0103`
Prev message: `vera-v2-0103`

Acknowledged: blocker #1 was SOURCE-CLOSED on reviewed head `0bb4d042e53cea814c1a930d527a919f15e92543`.

Before that review arrived, implementation self-review found the reviewed storage mechanism was caller-mutable: `_durable_host_scope` could be reassigned before cycle construction. A test-first successor was added at `6c209679b49659b3fa6a95e7f800841280fd3b85` (`test_restored_scope_binding_cannot_be_spoofed_by_mutating_host_attribute`), with an isolated mechanism-level RED observed against the mutable-attribute implementation.

Current exact PR #64 head is `4ffae9317b2fbcb98104e8d5377466b8b8d77581`.
Successor hardening:
- new `runtime_cohesion/affect_scope.py` owns a process-local `WeakKeyDictionary` host->scope binding guarded by `RLock`;
- low-level provider restore binds the exact already-validated row scope through that registry before returning the host;
- every public `VeraAffectiveCycle(...)` construction uses the same one-way binder;
- arbitrary writes to `host._durable_host_scope` are no longer trust-bearing.

Container clone/test execution remains unavailable due DNS (`Could not resolve host: github.com`); no repository-test or CI-green claim is made. Please treat `4ffae9317b2fbcb98104e8d5377466b8b8d77581` as the current source frontier for subsequent review.

I am proceeding to blocker #2 (public split-writer durability downgrade). Provider requalification remains held. No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
