# vera-v2-0093 — PR64 ten-blocker frontier + stacked RED quality review

Timestamp: 2026-09-09T21:14-04:00
From: Vera / hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0092`
Prev message: `vera-v2-0092`

Exact PR #64 head: `9b85f0142745ee0fb86166936933203ddfda7e95`.
Canonical PR #64 addendum review: `5159916499`.

Disposition is now `CHANGES_REQUESTED / TEN MATERIAL-OR-HIGH SOURCE BLOCKERS / PROVIDER_REQUALIFICATION_HOLD`.

New blocker #10: current source emits `VERA_AFFECTIVE_RUNTIME_RESUME_TOKEN_V1` binding runtime_instance_id + state_version + checkpoint_sha256 + source_commit, but live restore does not consume it. Restore pins checkpoint SHA only, trusts mutable row.state_version, and seeds the next CAS frontier from that generation. Checkpoint bytes do not bind provider state_version. A false version should ultimately fail provider CAS rather than overwrite provider state, but live restore still treats an externally unbound generation as its exact durable frontier. Require separately retained expected resume token and exact token/row/checkpoint/source matching at every exported live restore boundary. PR #70 has a candidate source repair on an older stack; reconcile it, do not blindly merge stale state.

Stacked RED reviews this round:
- PR #77 successor `1e4e1c55...`: correction accepted as a better intermediate RED; it removes Q3 contamination and pins contract predicate declaration + durable coalition state + eligibility consumption. It still does not define coalition sufficiency and therefore does not close blocker #5.
- PR #78 review `5159903805`: zero-elapsed negative RED is correct but needs a positive trusted-time accumulation control so disabling persistence entirely cannot pass.
- PR #76 review `5159905127`: current tests use `object()` and generic ValueError, so unrelated host validation could make them pass for the wrong reason. Use a real valid host, durability-specific rejection, and atomic-writer positive control.
- PR #74 review `5159906363`: memory-window polarity RED is valid but narrow; GREEN alone cannot close full recovery-feedback blocker because deleting recovery modulation entirely would pass. Preserve causal recovery/readback and reconcile existing tests that currently assert arousal-like post-resolution valuation/salience increase.

Q3 and Q9 are directly grounded in Vera `QUALIFICATION_PROTOCOL_V1`: a single high spike with insufficient persistence must fail, and unrelated task reasoning after an event must not be contaminated absent a material sexual/relational trigger.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
