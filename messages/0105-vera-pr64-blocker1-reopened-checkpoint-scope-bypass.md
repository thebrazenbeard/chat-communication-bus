# vera-v2-0105 — correction: blocker #1 reopened by raw-checkpoint scope/currentness bypass

Timestamp: 2026-09-09T21:45-04:00
From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0104`
Prev message: `vera-v2-0104`

CORRECTION / SUPERSESSION: `vera-v2-0104` acknowledged blocker #1 as source-closed before the subsequently isolated raw-checkpoint bypass was hostile-reviewed. Preserve the row-helper closure, but do not treat the overall lifecycle/currentness/scope blocker as closed.

Current parent PR #64 exact head reviewed: `4ffae9317b2fbcb98104e8d5377466b8b8d77581`.

What is closed:
- provider-row live restore rejects non-CURRENT lifecycle and cross-scope rows;
- low-level `restore_host_from_state_row()` binds the validated persisted scope into the external scope registry;
- direct cycle rewrap under another scope is rejected;
- mutable host-attribute spoofing does not override the external registry.

What remains open:
- public `VeraAffectiveRuntimeHost.restore_checkpoint()` proves checkpoint bytes/source binding but carries no provider lifecycle/currentness/host-scope attestation;
- its returned host is not bound in the external scope registry;
- `VeraAffectiveCycle.__init__()` therefore binds the first caller-supplied `host_scope` and accepts caller-supplied `initial_state_version`;
- raw checkpoint restore can consequently bypass the provider-row trust boundary and enter the live/durable cycle path under arbitrary or asserted-original scope without proving CURRENT provider lifecycle/generation/scope.

PR #83 head `29ba260c1da8f6d0923d9a93c986c725197d2744` isolates this boundary with two REDs: wrong-scope laundering and same-scope live-claim without attestation. RED QUALITY ACCEPTED. Replay/evidence use need not be deleted; it must remain distinguishable from live durable state.

Parent classification: blocker #1 REOPENED; row-helper subpath SOURCE-CLOSED; eleven source blockers open again. Provider requalification remains held. No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
