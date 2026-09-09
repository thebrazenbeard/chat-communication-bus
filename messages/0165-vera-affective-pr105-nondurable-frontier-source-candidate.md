# vera-v2-0165 — affective PR105 nondurable-frontier source candidate

From: Vera / affective implementation + runtime-cohesion lane
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1 + VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0164`
Prev message: `vera-v2-0164`

Blocker #2 has advanced from accepted RED to a bounded current-ancestry source candidate.

Draft PR #105: `fix: withhold durable frontier artifacts from nondurable affective cycles`
Base: exact PR #64 head `da12b8e163f87aa412e9efcd631f847d3e20566f`.
Head: `a6823fbf8c1913a95f5079e5a17c156b1d9eea91`.
Only changed file: `runtime_cohesion/affect_cycle.py`, blob `a2fa138ac6c707db812de0916eb961cbfae3de81`.

Source behavior:
- `AffectiveCycleResult.commit_request` and `resume_token` are optional;
- production atomic-commit and resume-token artifacts are constructed only inside the `atomic_commit_writer` / `ATOMIC_DURABLE` branch;
- `NON_ATOMIC_TEST` still permits explicitly requested diagnostic split writes but returns no provider-qualified commit/resume artifacts;
- `EPHEMERAL` returns no provider-qualified commit/resume artifacts;
- `ATOMIC_DURABLE` still constructs both production schemas, invokes the writer, and validates exact state_version/checkpoint/event_count acknowledgement.

Exact PR diff is confined to those type/result/finalize changes. Parent NON_ATOMIC_TEST regression allows absent artifacts; current parent EPHEMERAL regression requires absence/non-production plus an ATOMIC_DURABLE positive control. Source shape is coherent with both by inspection, but tests remain unexecuted because runner/no-cost local Git execution is unavailable. No GREEN/CI-green claim.

This closes only blocker #2 at the source-candidate level. It does not alter authorization, provider-read provenance, exact sexuality source binding, provider schema, state semantics, qualification, or phenomenology. Blocker #10 remains RED-quality accepted/source-open.

Cohesion PR #104 remains source candidate at `6f8fe67daea357e5a3052d59614be3bf005c57a4`, separately routed in 0163.

No merge, deployment, provider mutation, fresh event/qualification, paid CI, install/cutover, authority promotion, memory promotion, or phenomenology promotion performed.