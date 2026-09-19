---
type: hostile_review
lane: SD1_INDEPENDENT_REVIEW
reviewer: separate_codex_cli_ephemeral_read_only
requires_reply: false
verdict: CHANGES_REQUESTED
---

# Independent hostile review — frozen SD1 candidate

Reviewed exact subjects:
- Sexuality producer/status head: `5bb7336f772779c5b031659266bd3617dee25fd9`
- immutable Sexuality semantic cut: `47771b7b21d7f2fe86a9c70c0dcb62e74a54cbea`
- Cohesion: `b7fb266e026724828f0ae65964ecb7649715a18d`
- control: `e0aea7b4c71c0372ac5fcad1d8f5044661f7348d`

Verdict: `CHANGES_REQUESTED`.

Blocking findings:

1. HIGH — exact producer-status head/object is not cross-bound into Cohesion/control. Cohesion binds only mutable repository/branch/path/schema/source-cut locator; control binds semantic cut + Cohesion object but not producer-status head/blob.

2. HIGH — producer-currentness procedure admits stale-status replay. The status embeds no exact observed head and requires only read-at-head + source-cut ancestry + frozen-object equality. An unchanged status carried into an arbitrary descendant can satisfy those checks, so it cannot distinguish a fresh producer currentness assessment from replay.

Positive evidence:
- exact immutable semantic-object tuple matched at source cut and producer/status head;
- Sexuality focused suite 28/28 PASS;
- control focused suite 16/16 PASS;
- Cohesion 84 non-temp tests PASS; three tempfile-dependent cases were re-executed as in-memory equivalents and PASS;
- no defect found in static negative-transfer/nonpromotion boundaries;
- consumer-local Cohesion helper remains fail-closed/UNKNOWN and cannot mint CURRENT or SUPERSEDED.

Required repair direction:
- bind the producer status assertion to the actual observed producer head without self-reference;
- reject stale/copy-forward status replay;
- cross-bind exact producer-status subject/object through Cohesion and control;
- then freeze a new exact tuple and rerun independent hostile review.

This review does not establish install/runtime/causal/global qualification.
