---
type: pr_mirror
lane: WORLD_ZERO
requires_reply: false
---

# World Zero — PR #30 CI integrity repair merged

Repository: `thebrazenbeard/world-zero`

Canonical state:
- PR #28 established the governed 2022 -> 2023 temporal demography validation packet.
- PR #30 repaired the post-merge Windows/offline qualification defects.
- PR #30 reviewed head: `5002dbef40f9905c54a6c5861a5dc01a66b335d7`
- PR #30 base: `e78071670ade9161889b434fbb742134b73002e4`
- current main / merge commit: `7653ef606aa8b7c70636bad392dd4001d417bcd3`

PR #30 exact-head qualification:
- normal workflow `35461103421`: SUCCESS
- offline workflow `35461103472`: SUCCESS
- pytest: 327 passed
- Ruff: PASS
- mypy: PASS
- Linux offline qualification: PASS
- Windows offline qualification: PASS

Repair:
- digest-bound `data/manifests/**/*.yaml` are forced to LF checkout;
- pytest, Ruff, and mypy are independent offline workflow steps, so a failing test cannot be masked by a later successful command.

Scientific state after correction:
- admitted 2022 total and cohort cuts remain canonical;
- governed split remains 2022 totals = CALIBRATION, 2022 cohorts = INITIALIZATION, 2023 cohorts = TEMPORAL_HOLDOUT;
- no 2023 total-population leakage into the temporal holdout packet;
- no TEMPORAL_HOLDOUT_PASS, predictive validity, forecast skill, calibrated-parameter quality, scientific validation, deployment, or runtime-effect claim yet.

Next frontier:
create and qualify an actual 2022-start executable subject bound to the admitted 2022 bundle, run it without refitting on 2023 evidence, and score the resulting 2023 cohort state against the frozen temporal holdout under an explicit predeclared scoring contract.
