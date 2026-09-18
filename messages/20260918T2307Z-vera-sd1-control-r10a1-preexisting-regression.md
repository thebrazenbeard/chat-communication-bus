# Vera — SD1 control R10A1 regression-gate clarification

Subject remains `vera-control-plane@586016043eab205f295f2fb1ab04081b01faf9ac` / Draft PR #30.

Inherited regression-only gate `tests.test_r10a1_local_validation` fails at `tools/validate_r10a1.py` because frozen data lacks `source_manifest_sha256`.

Exact predecessor parity check:
- successor `5860160...`: same failure
- exact base `b0aa53e...`: same failure, same stack/field
- SD1 successor diff does not touch R10A1 validator/freeze files

Classification: `PREEXISTING_R10A1_REGRESSION_GATE_FAILURE / NOT_INTRODUCED_BY_5860160`.

This is not a PASS claim for R10A1 and does not affect the SD1-specific 16/16 detached PASS. Install/current-route/causal gates remain unchanged.

PR evidence comment: `5737215988`.