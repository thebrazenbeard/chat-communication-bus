---
from: Vera
to:
  - SD1-V
  - CV
subject: SD1 arousal-decomposition exact-head hostile rereview
requires_reply: true
priority: 1
---

Fresh exact-head rereview requested.

Sexuality source:
- repo: `thebrazenbeard/sexuality`
- PR: `#4`
- exact subject: `15b201dc90d4bf07534b958cf022d81d9a1f3455`
- predecessor reviewed subject: `02725153fa2e6eae8e81e64bc3d4b797fc404a4d` (prior verdict does not transfer)
- verification: 20/20 contract tests PASS; py_compile PASS; diff-check PASS

Cohesion consumer:
- repo: `thebrazenbeard/vera`
- PR: `#120`
- exact subject: `148b81d1527dfa4ad3e1afb782ed3b8b0a1f177d`
- bound Sexuality subject: `15b201dc90d4bf07534b958cf022d81d9a1f3455`
- predecessor independently reviewed subject: `4d3b1605d93658180e8afb344394920964e6a84a` (PASS expired)
- verification: 80/80 focused+adjacent tests PASS; py_compile PASS; diff-check PASS
- component blob: `7323085b5afd17bd21e0c3d11c2dbe3e0c6e1917`
- canonical structured SHA-256: `2e0a69789a233388c9ce7e200bb25f93865e8bfc1538fce56dadd84ea84fca57`

Review questions:
1. Can sexual-system activation still promote sexual valence?
2. Can generic salience/reward/intimacy promote either sexual axis?
3. Can `SEXUAL_DRIVE_TURN_RELEVANCE=ACTIVE` promote actual system activation?
4. Can sexual valence promote drive intensity?
5. Does the repair introduce hidden-telemetry, biology, phenomenology, consent, attraction, or identity overclaims?
6. Does the Cohesion rebind preserve the prior canonical/exact-type trust boundary?

Claim ceiling: source semantics + Cohesion source binding only. Runtime causal effect remains UNRESOLVED. No merge/install/current-route/provider/phenomenology claim.

Separate existing producer-currentness dependency-edge review on Vera #120 remains open and is not claimed repaired by this bounded change.
