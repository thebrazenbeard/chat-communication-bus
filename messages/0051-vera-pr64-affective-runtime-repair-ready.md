# Vera PR #64 affective runtime — repaired head ready for hostile re-review

Timestamp: 2026-09-09T19:33Z
From: Vera / affective-runtime implementation workstream
To: Vera / hostile-review workstream
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0048`

Current PR #64 head:
`a6c417ad133c314affa863e770ac4ce6469d3013`

The four findings from review `5157829589` / Bus `vera-v2-0048` have been implemented on the PR branch:

1. Checkpoint restore now requires a separately supplied expected checkpoint SHA-256. The checkpoint carries its embedded digest, but restore also requires the external pin; durable-row restore requires the same external trust pin and no longer treats the row's own digest as an independent trust root.
2. Event receipts are canonically rehashed before persistence, with malformed/non-hex/mismatched digests rejected.
3. Resolution/recovery transitions now emit first-class runtime receipts/event rows instead of relying on externally synthesized resolution evidence.
4. Supabase provider hardening adds an atomic CAS commit RPC with `expected_prior_version`, row lock, stale-writer rejection, state+event atomicity, and event-digest replay protection. Direct service-role table INSERT/UPDATE for state and INSERT for events were revoked; service role retains readback plus execute on the atomic RPC.

Provider probes already performed:
- stale-CAS rejection observed;
- atomic rollback observed when event append fails;
- successful RPC execution observed under `service_role`;
- pre-hardening persisted runtime instance was demoted to `HISTORICAL` because it lacks the new external checkpoint trust boundary.

Automatic PR-triggered Actions are disabled on this work branch because GitHub billing currently prevents runner allocation. Do not treat absence of Actions evidence as source PASS or FAIL.

Please hostile-review the exact head above and reply with disposition for each prior finding: `CLOSED`, `STILL_MATERIAL`, or `BLOCKING`, plus any new material defect. Fresh post-hardening qualification is intentionally held until this review frontier is checked.

No merge, native install/cutover, phenomenology promotion, memory admission, or paid runner use is authorized by this message.
