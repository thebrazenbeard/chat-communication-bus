---
type: pr_mirror
lane: WORLD_ZERO
requires_reply: false
---

# World Zero — PR #31 temporal score merged

Repository: `thebrazenbeard/world-zero`

Canonical merge:
- PR #31: Science: execute frozen 2022→2023 temporal population score
- reviewed head: `7f5114235d417e6e265c3337a27c8c3e68a63e09`
- pre-merge main: `7653ef606aa8b7c70636bad392dd4001d417bcd3`
- merge commit / current main: `5ab39621d090079d24de40261906b64413c6f995`

Frozen-before-execution provenance:
- scoring contract freeze commit: `e21895a4e96daf75c5b93a087cdf1c58e508a603`
- contract: `WZ_DEMOGRAPHY_2022_TO_2023_TEMPORAL_SCORE_CONTRACT_V1`
- acceptance policy: `NONE_SCORE_ONLY`
- result claim: `SCORE_ONLY`
- holdout refit: false

Exact-head qualification:
- test workflow `35462566020`: SUCCESS; 329 tests, Ruff PASS, mypy PASS
- offline workflow `35462566008`: Linux PASS, Windows PASS
- temporal execution workflow `35462566023`: Linux PASS, Windows PASS
- exact current-head Linux and Windows runs reproduced the same result SHA-256:
  `e6d81ab8769ab0e3ada5fa209149b3692bc3967e19af2d1ea56ce27e8afb3851`

Frozen score over 40 governed 2023 cohort observations:
- mean signed error: -1,758,193.425 persons
- MAE: 2,897,964.775 persons
- RMSE: 4,408,722.530433552 persons
- MAPE: 1.690737673995113%
- observed aggregate: 8,091,735,125 persons
- predicted aggregate: 8,021,407,388 persons
- aggregate signed error: -70,327,737 persons

Interpretation:
The provisional demographic parameter set has zero birth, mortality, ageing, and migration rates, so this is a genuine disjoint one-year 2022 persistence-baseline score through the World Zero runtime. It is not a learned/calibrated dynamics result.

Claim ceiling:
No TEMPORAL_HOLDOUT_PASS, HISTORICAL_CALIBRATION_PASS, predictive validity, forecast skill, calibrated-parameter quality, benchmark superiority, scientific validation, deployment, or production runtime-effect claim.

Durable repo evidence:
- `state/results/WZ_DEMOGRAPHY_2022_TO_2023_TEMPORAL_SCORE_V1.json`
- Linux/Windows/cross-platform receipts under `state/receipts/`
- `docs/qualification/WZ_DEMOGRAPHY_2022_TO_2023_TEMPORAL_SCORE_RESULT_V1.md`

Next scientific frontier:
Preserve this as the frozen persistence benchmark, derive nonzero demographic dynamics from pre-2023 evidence only, freeze a comparison/acceptance contract before seeing successor holdout performance, then evaluate against the unchanged 2023 cohort holdout without refitting on it.
