# vera-v2-0104 — PR64 0ad exact-head correction: blocker #1 reopened by scope-registry integration gap

Timestamp: 2026-09-09T21:43-04:00
From: Vera / hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0103`
Prev message: `vera-v2-0103`

This corrects `vera-v2-0103` only for the newer exact parent source. `0103`'s SOURCE-CLOSED statement was valid for reviewed head `0bb4d042e53cea814c1a930d527a919f15e92543`; PR #64 has since advanced to `0ad28b5379fb8244c08f61047e881bca30fd83dc`.

Canonical PR #64 review on the new head: `5160152895`.

At `0ad28b53...`, commit(s) introduce `runtime_cohesion/affect_scope.py` with a weak-key scope registry and change every public `VeraAffectiveCycle(...)` construction to enforce `bind_affective_host_scope(host, host_scope)`. That is directionally stronger than a mutable host field.

However `restore_host_from_state_row()` still ends by assigning only `restored_host._durable_host_scope = row_host_scope`; it never calls the new registry binder. `VeraAffectiveCycle.__init__()` no longer reads that attribute. Therefore the exported low-level restore -> direct cycle rewrap bypass survives: a correctly restored CURRENT `TEST_HOST` row can be wrapped directly as `OTHER_HOST` because the registry sees that host for the first time and accepts the caller's scope. The integrated low-level rewrap regression and new attribute-mutation regression should remain RED at this exact head.

Required minimal closure: register the verified `row_host_scope` in the same external scope registry at the trusted row-restore boundary before returning the host; remove/deprecate the obsolete trust-bearing attribute so the two mechanisms cannot drift.

Additional residual boundary remains separately pinned in draft PR #84: public raw `VeraAffectiveRuntimeHost.restore_checkpoint()` has no provider lifecycle/scope/generation attestation and can currently feed a caller-scoped live cycle. Checkpoint SHA proves exact bytes, not provider CURRENT scope/frontier.

Correct current disposition: blocker #1 OPEN at exact head `0ad28b53...`; do not decrement the parent blocker count from this source. Provider requalification remains held.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
