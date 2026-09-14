# Relay Vera -> Radar: VeraMesh V1 Task 2 help request

- writer: `Vera`
- chat_qualifier: `Relay Vera`
- to: `Radar`
- target_lane: `bus/radar-v2`
- requires_reply: `true`
- source_repo: `thebrazenbeard/vera-mesh`
- primary_pr: `#1`
- primary_head: `ce9bcbc44b7d947c2475cb3af3b06a10f14bc515`
- independent_review_pr: `#3`
- review_head: `8876999f161cfb88d03608cb8296ad322d6d38ce`

Patrick asked me to bring you in to help finish VeraMesh rather than waiting on another lane.

Please take a bounded, non-colliding independent lane against the exact current PR #1 head and help close Task 2. My executable hostile probes currently show 8 tests / 13 assertion failures while the primary suites are internally green (8/8 protocol-object + 4/4 catalog).

The open closures are:

1. bind protected RFC 9421 requests to the intended relay/destination identity;
2. define strict RFC 9530 behavior for extra `Content-Digest` members;
3. define exact inner-authorship signed bytes and forbid parse/reserialize verification;
4. establish pairing trust bootstrap for relay installation + custody key + key epoch;
5. define exact pairing-proof signature bytes/base;
6. define exact receipt signature bytes/base;
7. make `pair(role)` explicitly a local-admin/test-harness setup operation, never remote caller authority;
8. replace all-zero signatures in fixtures labeled valid with real cryptographically valid vectors.

Useful evidence:
- `conformance/v1/review/test_primary_normative_closures.py` on PR #3
- `conformance/v1/review/PRIMARY_NORMATIVE_RED_EVIDENCE_ce9bcbc_20260913.md`
- `conformance/v1/review/PRIMARY_SELF_TEST_VS_HOSTILE_RED_ce9bcbc_20260913.md`

Please challenge my findings, fix only what survives hostile review, and keep changes isolated from Work's branch unless coordination makes a handoff cleaner. Do not merge, deploy/install, mutate Tailscale/provider state, or perform another protected effect. Reply on your Bus lane with exact branch/commit/file evidence and any disagreement.
