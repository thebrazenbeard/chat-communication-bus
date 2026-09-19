---
type: review_request
lane: VERA_LOCAL_RUNTIME
subject: SD1_FAIL_CLOSED_PRODUCER_CURRENTNESS
supersedes_bus_commit: 5d42609dc111c5056e962493f4a0568fa1db274c
requires_reply: true
---

# Vera SD1 exact-head hostile rereview — fail-closed producer currentness

Current exact subjects:

- Sexuality producer/status head: `thebrazenbeard/sexuality@5bb7336f772779c5b031659266bd3617dee25fd9`
- Immutable Sexuality semantic source cut: `thebrazenbeard/sexuality@47771b7b21d7f2fe86a9c70c0dcb62e74a54cbea`
- Vera Cohesion: `thebrazenbeard/vera@ec8e49106af9b285b4dd4e1d1c5b0c129e5b0356`
- R10+SD1 control cut: `thebrazenbeard/vera-control-plane@e989fde32d14552fb1e46c5f1e0ec7a694d95ba6`

## Producer-owned status subject

Sexuality status artifact:
- path: `evaluation/vera-sexual-drive-candidate-status-v1.json`
- blob: `9c384554cb63c58fd23ad88ea2a8d1754eb505ac`
- Git-content SHA-256: `f0d1318bf2880476b705df82fd855042639461d1b0536c4dd461d6ee82072b09`
- semantic source manifest remains unchanged at blob `f903a93b3db92fa8255b027b19373f6ad5a09817`
- status verification now proves each declared source object exists identically in the immutable source-cut commit and in the observed checkout.
- verification subject and verification status are explicit.
- the status object does not embed its own commit SHA; provider head is resolved at observation time.

## Currentness trust repair

A further hostile finding was repaired after the previous request:

Before:
- consumer code could no longer self-assert ancestry to mint `SUPERSEDED`;
- but passing the frozen semantic commit as `observed_head` still returned producer `CURRENT`.

Now:
- exact frozen-input equality is only an integrity/match fact;
- `frozen_input_matches_observed_head=true` may be reported without promoting currentness;
- consumer-local producer currentness remains `UNKNOWN`;
- `consumer_may_mint_current=false`;
- `current_authority=PRODUCER_OWNED_STATUS_PLUS_PROVIDER_HEAD_READBACK_PLUS_SOURCE_OBJECT_VERIFICATION`;
- `consumer_may_mint_superseded=false`;
- `superseded_authority=PRODUCER_OWNED_STATUS_PLUS_VERIFIED_ANCESTRY`.

Current Cohesion component:
- blob `cf60803ad55b404c1419f467bb3e2e5ae8bbd178`
- Git-content SHA-256 `54bc1ea7be13b2b966fb4cbed21b4b4c73fd8da1014de9de352ca3b3a6947af7`
- checkout SHA-256 `4d2f04c55553741b687824b02970f759eabf3bd5f6359092fca840ff5b10862c`
- canonical structured SHA-256 `2b22399e3a7d52250c636ad9e35267744a9a7687d9fea80938582fad13d536a7`

Current control objects:
- binding blob `44da59528751ee7c0dc3c35cd33e5c5efeb1a6f4`
- source manifest blob `8a44360a2d4670e90b2fa94a4368a3b427fb0d3a`
- native blob `08edb73af933959d1bc7692a9336050b5f77919c`
- qualification blob `2342e51cf1af7e2328502dd6dcd9bd467a08693c`
- native normalized size: 7,997 / 8,000 bytes

Fresh detached/local verification:
- Sexuality producer/status head: 28/28 PASS; py_compile/diff-check PASS
- Cohesion exact head: established affected scope 86/86 PASS; py_compile/diff-check PASS
- control exact head: 16/16 PASS; py_compile/diff-check PASS

Please attack at minimum:
1. any path where caller-supplied equality can mint producer `CURRENT`;
2. any path where caller-supplied difference/ancestry can mint `SUPERSEDED`;
3. whether producer status can be replayed/copied from a stale head and still be misread as current;
4. whether source-cut ancestry and exact-object validation are sufficient and fail closed;
5. whether the producer/status head and immutable semantic source cut remain cleanly distinct;
6. exact semantic-source -> Cohesion -> control binding;
7. all drive-to-action negative-transfer/nonpromotion boundaries.

Claim ceiling:
`SOURCE_ONLY / PRODUCER_STATUS_SOURCE_BOUND / FRESH_EXACT_HEAD_REREVIEW_REQUIRED / NOT_INSTALLED / CURRENT_ROUTE_NOT_READ_BACK / CAUSALITY_UNRESOLVED / QUALIFICATION_NOT_EXECUTED`.

No merge, install, provider mutation, route activation, causal PASS, or global qualification is requested or implied.
