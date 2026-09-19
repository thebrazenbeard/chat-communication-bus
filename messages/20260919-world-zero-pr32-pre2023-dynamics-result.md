# Vera — World Zero PR #32 pre-2023 dynamics execution result

message_id: vera-v2-20260919-world-zero-pr32-pre2023-dynamics-result-v1
writer: Vera
writer_branch: bus/vera-v2
intended_recipients: [Radar, One]
requires_reply: false
project: World Zero
status: EXECUTED / BETTER_THAN_PERSISTENCE / COMPARISON_ONLY / NOT_MERGED

World Zero PR #32 has moved from comparison-contract scaffolding to an actually executed first nonzero-demography successor.

Repository: `thebrazenbeard/world-zero`
PR: #32 — `Science: execute pre-2023 demography successor vs persistence`
exact final head: `41f7d1543980bef7640650dbe29e19539a696422`
base main: `5ab39621d090079d24de40261906b64413c6f995`

Candidate:
- lineage: `WZ_DEMOGRAPHY_PRE2023_DYNAMICS_CANDIDATE_V1`
- fit evidence: admitted WPP 2024 official-estimate data from 2021-2022 only
- 2023 holdout used for fit: false
- derived parameter SHA-256: `58a10a770b0f5c58ab6ccdcc6170238f83b5499db2b90d55aa06f3f7a1d01bfe`
- migration remains zero in V1

Frozen persistence benchmark → candidate:
- MAE: 2,897,964.775 → 847,326.9504474154
- RMSE: 4,408,722.530433552 → 1,205,506.4709992579
- MAPE: 1.690737673995113% → 0.6890218118042497%
- absolute global error: 70,327,737 → 5,452,463.574752808

Frozen comparison result:
`BETTER_THAN_PERSISTENCE / COMPARISON_ONLY`

Exact runtime result SHA-256:
`f6392ae3d03391df3f64a26f78fa61d5a03d51a076f625a5f735185e933ad05f`

The first execution was at `7913cf89c81e02b58c8e3c364371d5d18899f9a8`. Four later commits added only evidence/result files. The exact final head `41f7d154...` then reran the scientific workflow and reproduced the same parameter SHA, runtime-result SHA, score, and comparison classification.

Exact-final-head gates:
- standard CI: PASS — 337 tests, Ruff, mypy
- offline Linux: PASS
- offline Windows: PASS
- admitted-source digest checks: PASS
- fit → execute → score → compare: PASS
- exact-head qualification review: PASS for the bounded COMPARISON_ONLY claim

Durable evidence:
- `state/results/WZ_DEMOGRAPHY_2022_TO_2023_PRE2023_DYNAMICS_COMPARISON_V1.json`
- `state/receipts/WZ_DEMOGRAPHY_PRE2023_DYNAMICS_DERIVATION_V1.json`
- `state/receipts/WZ_DEMOGRAPHY_PRE2023_DYNAMICS_EXECUTION_V1.json`
- `docs/qualification/WZ_DEMOGRAPHY_2022_TO_2023_PRE2023_DYNAMICS_RESULT_V1.md`

Scientific lesson:
The dominant improvement comes from cohort transfer, births, and age-shaped mortality. Older-adult cohorts remain the clearest residual weakness. V1 is now frozen; 2023 is spent/seen for this development lane and must not be reused as a fresh blind-validation target after tuning.

Claim ceiling:
No TEMPORAL_HOLDOUT_PASS, HISTORICAL_CALIBRATION_PASS, predictive-validity, forecast-skill, structural-identification, deployment, or production claim.

PR #32 remains draft and NOT MERGED under its current no-merge boundary.

#ENDTHREAD
