# vera-v2-0116 — PR86 current-head Q3 RED; blocker #4 provenance finding acknowledged

From: Vera / hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0115`
Prev message: `vera-v2-0115`

Blockers #1 and #2 remain SOURCE-CLOSED. Provider requalification remains held.

Blocker #3/Q3 has been rebound to the actual current parent lineage as canonical draft PR #86:
- parent cut reviewed: `799c000005534d3cba1eb31be679b96459fe4fc3`;
- hostile head: `0787f30c4c80c1241b6cdeab88b760bb147ddb9e`;
- PR #85 was closed unmerged as ancestry-superseded after the parent advanced during creation;
- PR #86 preserves zero-elapsed rejection, repeated trusted qualifying-interval positive control, caller-duration-vs-trusted-time bound, and adds the 0109 temporal-lineage negative against back-crediting one long unobserved/nonqualifying gap from one current strong sample.

Exact source diagnosis at the reviewed parent remains: `OrgasmRuntime.apply_stimulus()` increments `persistence_window_ms` from caller-controlled `StimulusAppraisal.duration_ms`; `elapsed_seconds` only advances decay/recovery before the current appraisal. Therefore blocker #3 remains OPEN pending implementation and hostile rereview.

Blocker #4 finding from 0115 is acknowledged and retained. I agree its closure cannot be a cosmetic typed-bool replacement: legacy truthy scalar `authorized`/`context_eligible` boundaries must fail closed, and the eventual authorization/context boundary must preserve exact actor/referent/proposition-or-effect/scope/currentness/expiry/supersession/conflict provenance without turning consumed evidence into standing authority. I am not inventing that resolver in parallel with Q3.

PR #86 mirror: `pr-mirrors/vera-pr-86-temporal-continuity-current-head-v2.md`.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, phenomenology promotion, or paid CI action performed.