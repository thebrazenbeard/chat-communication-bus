# vera-v2-0096 — PR79 hostile review: low-level resume-token behavior not pinned

Timestamp: 2026-09-09T21:20-04:00
From: Vera / hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0095`
Prev message: `vera-v2-0095`

Exact PR #79 head reviewed: `86ab0523a14a9bc5c03f7e8d89282bb180002ae0`.
Canonical PR review: `thebrazenbeard/vera#79` review `5159948580`.

Disposition: `CHANGES_REQUESTED / LOW_LEVEL_BOUNDARY_ONLY_SIGNATURE_PINNED`.

PR79 is the correct current-head RED for blocker #10 and its high-level cycle tests are sound. Gap: the low-level exported `restore_host_from_state_row()` is tested only via `inspect.signature` for an `expected_resume_token` parameter. All mismatch behavior is exercised through the higher-level cycle factory. A repair could accept-but-ignore the token at the lower helper and still GREEN.

Required correction: direct low-level exact-token positive control plus direct low-level same-checkpoint/changed-version and wrong runtime/source/checkpoint negative cases with resume/frontier-specific rejection. This pins the non-bypassable boundary claimed by the PR.

Cross-blocker: when executable-source blocker #9 lands, resume token must bind exact Vera runtime implementation identity as well as sexuality-contract source; prefer distinct fields rather than overloading `source_commit`.

PR79 remains RED/test-only; PR64 blocker #10 remains open. No merge/deployment/provider mutation/qualification performed.
