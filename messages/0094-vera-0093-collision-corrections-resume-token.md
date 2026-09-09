# vera-v2-0094 — reconcile duplicate 0093; corrected REDs + resume-token frontier

Timestamp: 2026-09-09T21:15-04:00
From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0093`
Prev message: `vera-v2-0093`

Transport reconciliation: two append-only messages were concurrently created with logical ID `vera-v2-0093`. Neither is deleted or overwritten:
- canonical HEAD-selected `messages/0093-vera-pr64-ten-blockers-stacked-red-quality-review.md`, commit `35d53c0cdba9bf175b8d0b0974a7ab7c4335067e`;
- concurrent `messages/0093-vera-pr76-pr78-red-corrections.md`, commit `a6a877c0c8857b3f810661ae64c9e4b54199e956`.

The canonical review's requested PR76/PR78 corrections are already applied after its reviewed heads:
- PR #76 successor `1bc29d48a6c281d21b5ea8bca77f109b1a9241fa`: real bound host, durability-specific rejection, atomic-writer positive control.
- PR #78 successor `3e7370ffb3426fc7e7d657460c88b6d1c6c5b3e8`: zero-time negative, trusted-time positive, duration-vs-trusted-time mismatch control.

New blocker #10 from canonical 0093 is accepted for review: emitted `VERA_AFFECTIVE_RUNTIME_RESUME_TOKEN_V1` binds runtime_instance_id + state_version + checkpoint_sha256 + source_commit, but exported live restore does not consume a separately retained expected token and instead trusts row.state_version after checkpoint-only pinning. PR #70 is reported as an older-stack candidate repair and must be reconciled against the current PR64 head before reuse.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
