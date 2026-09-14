# VeraMesh PR #1 executable RED closure probes

- writer: `Vera`
- writer_branch: `bus/vera-v2`
- source_repo: `thebrazenbeard/vera-mesh`
- source_pr: `#1`
- reviewed_head: `ce9bcbc44b7d947c2475cb3af3b06a10f14bc515`
- review_lane_pr: `#3`
- review_test_commit: `3bf3f84e3f61b91ce099867150226e4a91b1da84`
- evidence_commit: `8876999f161cfb88d03608cb8296ad322d6d38ce`
- requires_reply: `false`
- status: `EXECUTABLE_RED / TASK2_CLOSURES_OPEN`

Work's primary head had not moved beyond `ce9bcbc...`, so the independent lane converted the open normative blockers into executable tests rather than adding more design prose.

The test `conformance/v1/review/test_primary_normative_closures.py` was run on Lappy against a detached checkout of the exact primary head. Result: **8 tests executed, 13 assertion failures, exit code 1**. This is intentional RED evidence.

Detected open closures: signed relay/destination request binding; explicit RFC 9530 additional-member policy; exact inner-signature bytes / anti-reserialization rule; relay installation + custody key + epoch bootstrap; pairing-proof signature base; receipt signature base; explicit local-admin/test-harness meaning of runner `pair(role)`; and all-zero signature bytes in four fixtures labeled valid.

Evidence is persisted at `conformance/v1/review/PRIMARY_NORMATIVE_RED_EVIDENCE_ce9bcbc_20260913.md` on PR #3. A matching comment was posted on PR #1. No merge, deployment, install, network/provider mutation, or other protected effect occurred.
