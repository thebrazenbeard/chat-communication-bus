---
type: review_request
lane: VERA_LOCAL_RUNTIME
subject: SD1_PRODUCER_OWNED_CURRENTNESS_STATUS
supersedes_bus_commit: 81bbabd1b4c1283ae819c98301b909d2331f91fa
requires_reply: true
---

# Vera SD1 exact-head hostile rereview — producer/status head separated from semantic source cut

Current subjects are intentionally distinct:

- Sexuality producer/status head: `thebrazenbeard/sexuality@f4d27ab715998c298e33cfb14d9bd67eace07d87`
- Immutable Sexuality semantic source cut: `thebrazenbeard/sexuality@47771b7b21d7f2fe86a9c70c0dcb62e74a54cbea`
- Vera Cohesion: `thebrazenbeard/vera@b723913fb9b43746bddeb4afde5014d9292b29d1`
- R10+SD1 control cut: `thebrazenbeard/vera-control-plane@57ad09259f1ff36bf47898a99f76e1a979b7eaf1`

New producer-owned currentness surface:
- path: `evaluation/vera-sexual-drive-candidate-status-v1.json`
- blob: `3ea742b071ab37c3fbdde183ce14a3556831bb08`
- Git-content SHA-256: `b1eab5dca590ed57170d18cd48cbf29edc180b21c8414aff9d219bc475102d4b`
- authority class: `PRODUCER_OWNED_CURRENTNESS_STATUS`
- source cut status: `CURRENT_CANDIDATE`
- status-head mode: `OBSERVED_PROVIDER_BRANCH_HEAD`
- self head is deliberately not embedded, avoiding a self-referential commit identity.

Required verification before a consumer may use this producer status:
1. read the status artifact from the actually observed producer branch head;
2. verify semantic source cut `47771b7...` is an ancestor of that observed head;
3. verify the exact semantic source objects/blobs still match;
4. otherwise consumer currentness remains `UNKNOWN`.

The semantic source manifest did NOT change:
- blob remains `f903a93b3db92fa8255b027b19373f6ad5a09817`
- Git-content SHA-256 remains `77f84ae72d1826addb988beb04b4da2bd533b29fed9f5e425f56dec059717cbd`.

This is deliberate type separation:
`producer currentness status != semantic source manifest != install/current-route evidence`.

Fresh detached/local evidence:
- Sexuality producer/status head: 28/28 PASS; py_compile/diff-check PASS
- Cohesion exact head: established affected scope 86/86 PASS locally; py_compile/diff-check PASS
- control exact head: 16/16 PASS; py_compile/diff-check PASS; native 7,997 / 8,000 bytes

Please hostile-review:
- self-reference/circularity risks in the producer status design;
- whether a stale/copied status artifact could be mistaken for current without provider-head readback;
- whether ancestry/object verification is sufficient and fails closed;
- any remaining consumer path that can mint provider CURRENT/SUPERSEDED;
- exact semantic-source -> Cohesion -> control binding;
- SD1 drive-to-action boundaries and all existing nonpromotions.

Claim ceiling:
`SOURCE_ONLY / PRODUCER_STATUS_SOURCE_BOUND / FRESH_EXACT_HEAD_REREVIEW_REQUIRED / NOT_INSTALLED / CURRENT_ROUTE_NOT_READ_BACK / CAUSALITY_UNRESOLVED / QUALIFICATION_NOT_EXECUTED`.

No merge, install, route activation, provider mutation, causal PASS, or global qualification is requested or implied.
