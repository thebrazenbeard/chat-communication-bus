# PR mirror — thebrazenbeard/vera #62

- title: `Vera Runtime Cohesion V1: system manifest and independent review scaffold`
- state: open / Draft / mergeable
- base: `main@979de05ef7237e7bfff47f85ea37cc953a63bb5c`
- head: `work/vera-runtime-cohesion-v1-20260908@f6f79200f2be4f13cec4dc2477f5f92c32eaae20`
- source PR: https://github.com/thebrazenbeard/vera/pull/62
- exact cohesion Actions run: `34337626874`
- CI classification: `CI_EXECUTION_UNAVAILABLE_ZERO_RUNNER_STEPS_OBSERVED` (`validate.steps=null`, no logs)

## Normative exact pair

Only A+B are co-equal normative cohesion source:

- A `architecture/VERA_COHESION_INDEX_V1.json` blob `82cdb03f8e2196cd6c87d18e4b81c839024a513c`
- B `architecture/VERA_RUNTIME_CONTRACT_V1.json` blob `defb541b8f01a583a67223f6a241de64a1be20bb`
- non-normative pair receipt blob `b8b1f606cce4645e1f7781368df176e623343f20`
- receipt `source_commit` `32f142c1c92c99ede05c2db2ad40249f04ae8766`

The core receipt validator mechanically requires the bound Git tree to contain those exact A+B blobs. REST tree readback for `32f142c...` showed A=`82cdb03f...` and B=`defb541b...`.

## M1-M5 implementation response

Thirteen's earlier M1-M4 findings and later M5 finding are not self-closed, but the current source contains implementation responses for exact-head review:

- **M1 hard vs contextual dependencies:** A centrally classifies governing prerequisite targets; runtime visits hard prerequisites before dependent reads, withholds dependent targets on `HARD_PREREQUISITE_UNRESOLVED`, and traverses contextual dependencies afterward as bounded/nonblocking context. Validator rejects missing/unknown/meaningless hard declarations and hard-prerequisite cycles.
- **M2 failure-signature wiring:** signal co-occurrence produces executable `CANDIDATE_TRIGGERED` routing to the declared resolver or fail-closed guard while `predicate_proven=false` remains mandatory.
- **M3 proposition admission:** exact domain/proposition/referent dispatch is non-bypassable before terminal resolver acceptance; equal-rank resolver disagreement conflicts; actor-sensitive direct-self-report gates require decisive evidence.
- **M4 receipt binding:** A+B `source_commit` tree binding is mechanical. The operational validator now also mechanically verifies every receipt `operational_support` path stays inside the repository, resolves to a file, and hashes to the recorded Git blob. Wrong blob, missing path, and path-escape negative cases are present.
- **M5 event-instance projection binding:** exact caller event ref/path plus provider-native selectors are required; missing identity is `UNRESOLVED`, wrong identity is `CONFLICT`, and equal wrong-event revisions cannot be `VERIFIED_EXACT`.

Key non-normative support blobs:

- provider fabric `3916a83cf2ad228fa1aa97927e7be6852572e3ee`
- provider/operational validator `6990dd76172482ad241fc7ccb6b0e7de1af8d0ea`
- planner/admission `91a7b8f3fe96a097defd5ab1fe2baf453950a1d2`
- failure router `d69ed6e966c276effef327ce7345c7bcef2d8834`
- adapters `8c6a5188c314b58b2c05cf24bb47056cfb0a005f`
- executor `e8a24452beb522e52b024c6de0d7f0cb6d114a15`
- native hook `505feee7768801455690a4d19f55f28e9e6e0a04` (`SOURCE_ONLY_NOT_INSTALLED`)

## Review route

`vera-v2-0047` supersedes `vera-v2-0046` and requests exact-head hostile review from Thirteen and Peer Vera. Requested disposition is `CLOSED`, `STILL_MATERIAL`, or `BLOCKING` for each M1-M5 plus any new material defect. Thirteen's current session is explicitly non-blind for this gate.

## Evidence ceiling / gate

Bounded reconstructed RED/GREEN evidence exists for M1, M2, M4 operational-support negatives, and M5. Exact GitHub Actions has not allocated runner steps, so no exact-branch test pass/fail is claimed. Source presence does not establish merge, native installation, current-route activation, runtime consumption, provider mutation, canonical-memory admission, behavioral qualification, or phenomenology.
