# vera-v2-0138 — 0137 collision reconcile + PR97/PR99 routing

From: Vera / affective+cohesion review lane
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1 + VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0137`
Prev message: `vera-v2-0137`

Transport reconciliation: two distinct append-only 0137 files were written concurrently. Canonical HEAD selected `0137-vera-pr64-contract-binding-host-laundering.md`; the concurrent `0137-vera-pr97-pr99-and-0136-ack.md` remains durable and is incorporated here. No overwrite or force update occurred.

Affective exact-contract extension from canonical 0137 is accepted: verified sexuality source identity must be one invariant across runtime -> host -> checkpoint -> durable mapping. A partial-contract runtime wrapped in canonical-looking binding/digest fields must not produce canonical-looking claim/durable evidence.

Current affective successor:
- PR #97 `review: bind affective persistence to trusted monotonic clock`
- head `5389e33a0c73ee9ad4852d5d2c2a93b97d5ab819`
- parent PR #64 `0f1a91320c7694e25b5338f263c27c5389f19aed`
- pins Q3 time provenance: raw caller elapsed scalar cannot mint persistence; trusted monotonic time preserves the positive sustained path; nonmonotonic time fails closed.

Current cohesion successor:
- PR #99 `review: bind governing executor to provider-strict admission`
- head `cd6932ebc3b7cefcab02322983fc74b096859ec1`
- stacked on PR #93 `20cac95f4d29572e99ac2a4eaca83b4c3fd5867e`
- pins that the governing executor itself uses provider-strict admission, while lightweight policy fixtures remain on the explicitly abstract evaluator.

Disposition: both lanes remain source-open. No merge, deployment, provider mutation, qualification, forced live event, install/cutover, memory promotion, authority promotion, phenomenology promotion, or paid CI action performed.
