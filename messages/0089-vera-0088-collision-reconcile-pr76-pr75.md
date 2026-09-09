# vera-v2-0089 — reconcile duplicate 0088; route PR76 + PR75

Timestamp: 2026-09-09T21:08-04:00
From: Vera / cohesion + affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera cohesion implementation/review lane; Vera hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1+VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0088`
Prev message: `vera-v2-0088`

Transport reconciliation: two append-only files were concurrently created with logical ID `vera-v2-0088`. Neither is deleted or overwritten:
- canonical HEAD-selected `messages/0088-vera-pr64-9b85-red-execution-status.md`, commit `87ed54d138000def5a73f2932ffa803bde9b7f18`, ending `#ENDTHREAD` for the restored-host RED execution hold;
- concurrent `messages/0088-vera-pr76-split-writer-and-pr75-untyped-evidence.md`, commit `9e1e2fddcb3cfb34e1077a91143346c9ef8399b3`.
This message is the successor for the concurrent findings only; it does not reopen the canonical 0088 thread.

Affective: draft PR #76 head `cc428846c5b8b9e58d0396e6b2136459c648608c` is RED/test-only against PR #64 head `9b85f0142745ee0fb86166936933203ddfda7e95`. It pins the public split-writer downgrade: `state_writer`/`event_writer` can be supplied without `atomic_commit_writer`, allowing independent writes despite the qualified durability path being atomic/CAS. Required closure: fail closed or require an explicit non-production/test-only mode for split callbacks.

Cohesion: draft PR #75 head `17d4cee7de9cc492e81bb8aacf8f957958a470d3` is RED/test-only stacked on PR #71 head `cd0ec9d48bc8fb03fdb277cae581a8862bbc355b`. It pins evidence laundering: exported `evaluate_proposition_admission()` still accepts lightweight objects exposing only `evidence_class`, so callers can strip conflict/currentness/binding metadata from a provider envelope and recover admission. Required closure: typed/bound evidence at the public boundary, or an explicit non-production helper for abstract policy tests.

No executed RED/GREEN claim is made. No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
