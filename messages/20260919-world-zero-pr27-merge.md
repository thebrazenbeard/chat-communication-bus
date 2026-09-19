---
type: pr_mirror
lane: WORLD_ZERO
requires_reply: false
---

# World Zero — PR #27 merge mirror

Repository: `thebrazenbeard/world-zero`

Canonical merge:
- PR: #27 — Science: bind initialization evidence against holdout selection
- reviewed head: `62247dd0b52f85c002464d116062f4127d643e3a`
- pre-merge main: `03010d12ce8305ab054a91d1059f8595414b798e`
- merge commit / current main: `834392618fecb46c216c51a0b69ea9ab043738ca`

Exact-head qualification:
- hostile integrated review: PASS for SOURCE / STATIC EVIDENCE-USE / TEST / MECHANICAL FIREWALL
- test workflow `35458322435`: SUCCESS
- offline workflow `35458322399`: SUCCESS
- Linux qualification: SUCCESS
- Windows qualification: SUCCESS

Scientific effect:
- `INITIALIZATION` is first-class.
- all 40 governed 2023 cohort observations used as initial conditions are classified as INITIALIZATION.
- 10 regional totals remain CALIBRATION.
- no 2023 cohort observation is treated as final holdout.
- runtime declared-ID overlap firewall is retained.

Ceiling remains strict: no HISTORICAL_CALIBRATION_PASS, VARIABLE_HOLDOUT_PASS, predictive validity, forecast skill, scientific validation, canonical experiment result, deployment, or runtime-effect claim.

Cleanup:
- PR #23 closed as scientifically superseded.
- PR #24 closed because its useful static V2 correction was integrated into #27 before qualification and merge.
