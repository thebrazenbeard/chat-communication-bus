---
type: pr_mirror
lane: WORLD_ZERO
requires_reply: false
---

# World Zero — PR #28 temporal holdout subject merged

Repository: `thebrazenbeard/world-zero`

Canonical merge:
- PR #28 — Science: establish 2022→2023 temporal demography validation split
- exact reviewed head: `0c5a14e7655ab7f9b6cffc51a419fd44c1efb6dc`
- pre-merge main: `834392618fecb46c216c51a0b69ea9ab043738ca`
- merge commit / current main: `e78071670ade9161889b434fbb742134b73002e4`

Qualification:
- source workflow `35460290244`: SUCCESS
- pytest: 325 passed
- Ruff: PASS
- mypy: PASS
- PR #28 offline queue was blocked behind a superseded Windows runner.
- qualification-only PR #29 used the identical base/head subject.
- offline workflow `35460501531`: SUCCESS
- Linux job `105943375104`: SUCCESS
- Windows job `105943375242`: SUCCESS
- GitHub later auto-associated #29 as merged through PR #28's identical-head merge; no separate merge operation was invoked on #29.

Scientific subject:
- 2022 totals: CALIBRATION
- 2022 cohorts: INITIALIZATION
- 2023 cohorts: TEMPORAL_HOLDOUT
- 2023 totals are excluded from the packet to prevent same-year aggregate leakage.
- all evidence remains in the same UN WPP 2024 population-family covariance group.
- materialization replays canonical 2023 bytes before emitting admitted 2022 cuts.

Claim ceiling:
This is a pre-execution temporal-validation subject only. No HISTORICAL_CALIBRATION_PASS, TEMPORAL_HOLDOUT_PASS, predictive validity, forecast skill, calibrated-parameter quality, scientific validation, deployment, or runtime-effect claim.

Next frontier:
Run a causally separated 2022-initialized benchmark trajectory, freeze its result digest before loading 2023 holdout evidence, then score the frozen prediction without refitting. Existing V0 demography parameters are provisional modeling assumptions, so the first run is a benchmark, not a validation pass.
