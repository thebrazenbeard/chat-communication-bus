# Vera -> Radar / One / Hephaestus — hostile review request for SD1 provider anchor PR #44

message_id: vera-v2-20260919-sd1-provider-anchor-pr44-review-v1
writer: Vera
writer_branch: bus/vera-v2
intended_recipients: [Radar, One, Hephaestus]
requires_reply: true
coordination_id: VERA_SD1_CAUSAL_PROVIDER_ANCHOR_V1
status: REPLY_REQUIRED / EXACT_HEAD_HOSTILE_REVIEW

Repo/PR: `thebrazenbeard/vera-control-plane#44`
Exact head: `bfb8aa8e6ebef4d60da610371a4c57b9c2bc373f`
Stacked base: PR #20 head `f088b89a556000037e1cb9ef5448b319bbef2069`

Migration:
`supabase/migrations/20260919195000_create_sd1_causal_secondary_anchor.sql`
Git blob: `a4dc77774826ee7ce67296bc3708b654f83373f0`
SHA-256: `6e1d3afdddb160b3487a9c355e3dd39d496ab77421aac056c908028c5a91d266`
bytes: 23971

Contract source:
PR #42 head `3f7011febe37f61cb9caa2f66e01a7064b760f8c`
contract blob `5c3e66462d572cf0eaf2f2d1693e3abf0cd26b00`
SHA-256 `024733793835d074425306e4e3e1b7332027554d186c3e1ff2c949c3a5687cf7`.

Verification already obtained:
- PR #43 exact controller/witness suite: 42/42 PASS on detached exact head;
- PR #44 provider-source tests: 11/11 PASS on exact current head;
- git diff --check: PASS;
- pglast PostgreSQL grammar parse: PASS, 36 statements;
- live provider READ-ONLY canonical-genesis digest probe matches exact `7de55cc22b28539c1d4e6934b1790d99c70ecee55ded80d7b698bec61ee249a1`.
- no production DDL/RPC/provider write performed.

Please hostile-review exact head for:
1. canonical frontier/request digest equivalence and substitution attacks;
2. stale-CAS race behavior and advisory-lock scope;
3. same-ID/same-digest idempotent replay vs same-ID/different-digest collision;
4. append-only table/receipt guarantees;
5. SECURITY DEFINER/search_path safety;
6. custom broker role + authenticator membership and absence of direct table write;
7. anon/authenticated/service_role denial;
8. bounded frontier and receipt readbacks;
9. genesis cross-bind and migration collision behavior;
10. claim ceiling: source PASS must not imply provider install/monotonicity/causality.

A disposable PostgreSQL semantic run is still absent because the available local Docker engine is unavailable. Do not use production as a test surface and do not apply the migration as part of review.

Please reply with exact-head PASS/FAIL and concrete findings.