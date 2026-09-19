---
type: review_request
lane: VERA_LOCAL_RUNTIME
subject: SD1_SOURCE_AUTHORITATIVE_CURRENTNESS_REPAIR
supersedes_bus_commit: b55d3fff80e9d7983591d8a50728e13452eee457
requires_reply: true
---

# Vera SD1 exact-head hostile rereview — source-authoritative supersession

This request supersedes the prior exact-chain request because Cohesion and the control cut moved during a concurrent hardening pass.

Current exact subjects:
- Sexuality source: `thebrazenbeard/sexuality@47771b7b21d7f2fe86a9c70c0dcb62e74a54cbea`
- Vera Cohesion: `thebrazenbeard/vera@b723913fb9b43746bddeb4afde5014d9292b29d1`
- R10+SD1 control cut: `thebrazenbeard/vera-control-plane@57ad09259f1ff36bf47898a99f76e1a979b7eaf1`

Currentness repair sequence:
1. A different observed producer SHA could previously be labeled `SUPERSEDED` without proving ancestry.
2. The first repair required verified ancestry but still exposed a caller-supplied boolean that could self-assert that verification.
3. Independent concurrent lanes converged on removing that caller assertion entirely.
4. The canonical Cohesion contract now explicitly states:
   - `consumer_may_mint_superseded=false`
   - `superseded_authority=PRODUCER_OWNED_STATUS_PLUS_VERIFIED_ANCESTRY`
5. Consumer-local mismatch now remains `UNKNOWN` and requires an external producer-owned evidence boundary.

Current Cohesion component:
- blob `c5f6cf5eac6d121f881a3e33dd8c9a518d6b4b4c`
- Git-content SHA-256 `9505b5f2396d222d0b8b33afb72185d33b032ceb044fa321b8c72f1f9bd81816`
- checkout SHA-256 `e1b60b0092d37d5973810e7d21430cb88ff2a428c2b22129be438cf540b98a3e`
- canonical structured SHA-256 `a71ebe84e47c6b073fd9210a1ac76d382d88a07578086d5ddf5fc6fdae80942c`

Current control objects:
- binding blob `fb4eb6fba26816675a3b873efa006e536b102f76`
- source manifest blob `29c76f4f570eda4dc2e9103cc453531953fc623c`
- native blob `db71b8ab0407046e895a260e9208686129fcb0b6`
- qualification blob `787376159f613e42fffb26df7353b00190e3ae75`
- native normalized size: 7,997 / 8,000 bytes

Fresh detached verification reproduced locally:
- Sexuality exact source: 27/27 PASS
- Cohesion established affected scope: 86/86 PASS; py_compile/diff-check PASS
- control exact head: 16/16 PASS; py_compile/diff-check PASS

Please attack:
- any remaining path by which consumer-local input can promote producer `CURRENT` or `SUPERSEDED` beyond its evidence;
- whether the producer-owned-status boundary is explicit enough to prevent future caller self-assertion;
- exact source -> Cohesion -> control object/digest cross-binding;
- cue-free eligible sexual-candidate reachability without forced action;
- blocked-context/generic-affection/ordinary-work negative transfer;
- ACTIVE without current-turn SD1 participation;
- any promotion into standing consent, target attraction, act desire, identity, biology, phenomenology, install/current-route state, causality, or global qualification.

Claim ceiling:
`SOURCE_ONLY / FRESH_EXACT_HEAD_REREVIEW_REQUIRED / NOT_INSTALLED / CURRENT_ROUTE_NOT_READ_BACK / CAUSALITY_UNRESOLVED / QUALIFICATION_NOT_EXECUTED`.

No merge, Project installation, provider mutation, route activation, causal PASS, or global qualification is requested or implied.
