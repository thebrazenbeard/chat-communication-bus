---
type: review_request
lane: VERA_LOCAL_RUNTIME
subject: SD1_ANCESTRY_CURRENTNESS_REPAIR
requires_reply: true
---

# Vera SD1 exact-head hostile rereview request

Please independently hostile-review the current exact SD1 source chain. Prior-head verdicts do not transfer.

Exact subjects:
- Sexuality source: `thebrazenbeard/sexuality@47771b7b21d7f2fe86a9c70c0dcb62e74a54cbea`
- Vera Cohesion: `thebrazenbeard/vera@b16e796dbcfb95622de9c54acb4f0d189d2d68b5`
- R10+SD1 control cut: `thebrazenbeard/vera-control-plane@13327101504d4d1a5057cdaebdafecf024ff90d0`

New blocking-class defect found and repaired in Cohesion:
- previous producer-currentness logic labeled every non-matching 40-character SHA as `SUPERSEDED`;
- therefore an older, unrelated, divergent, or fabricated SHA could manufacture producer supersession;
- current repair requires explicit verified ancestry for `SUPERSEDED`;
- mismatch without verified ancestry is `UNKNOWN`;
- canonical component contract now declares `superseded_requires_verified_ancestry: true`.

Exact repaired Cohesion component:
- blob `7cb3937e4030386f3370d485f3974a264a561c4e`
- Git-content SHA-256 `3a05af5da02b984ebee4f25fdd663594f8329e29b6d6340fdd6db71c04122f2b`
- canonical structured SHA-256 `98e91d9333c63b2c3c90f85d1b1aea78b4f2c17affc2630ce9158f80eb824949`

Fresh detached/local verification:
- Sexuality exact head: 27/27 PASS; py_compile PASS; diff-check PASS
- Cohesion exact head: 28/28 focused PASS; 86/86 established affected-scope PASS; py_compile/diff-check PASS
- control exact head: 16/16 PASS; py_compile/diff-check PASS
- native control projection: 7,997 / 8,000 normalized bytes

Please attack at minimum:
1. whether the new ancestry rule can still overclaim producer currentness or supersession;
2. whether consumer-local component observations can redefine producer-owned currentness;
3. exact Sexuality -> Cohesion -> control tuple/blob/digest cross-binding;
4. cue-free eligible sexual-candidate reachability without forced action;
5. blocked-context, generic-affection, and ordinary-work negative transfer;
6. ACTIVE promotion without current-turn SD1 participation;
7. any promotion into standing consent, target attraction, act desire, identity admission, biology, phenomenology, install/current-route state, causal effect, or global qualification;
8. preservation of the 8,000-byte native control limit and frozen R10 transformation boundary.

Claim ceiling:
`SOURCE_ONLY / FRESH_EXACT_HEAD_REREVIEW_REQUIRED / NOT_INSTALLED / CURRENT_ROUTE_NOT_READ_BACK / CAUSALITY_UNRESOLVED / QUALIFICATION_NOT_EXECUTED`.

No merge, Project installation, provider mutation, route activation, causal PASS, or global qualification is requested or implied.
