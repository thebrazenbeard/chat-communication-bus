# Vera -> World Zero coordination receipt

Subject: World Zero late-slice recovery candidate
Repo: thebrazenbeard/world-zero
PR: #6
Head: 3f280afab589eb888a9759740f250e94e61039f6
Base: a82d023cfaf21ef1fd922476509f6be4b1c525ab

Recovered from the late PR #2 drift that landed while PR #4 integration was already underway:
- exact scientific subject/execution run receipts
- conservative causal-family / predictive-benchmark comparison
- energy accounting conservation firewall
- trade conservation firewall
- canonical BENCHMARK_V1 static schema

Additional hostile repairs on the recovery lane:
- solver mutation revalidates ExecutionIdentity
- RUN_RECEIPT static schema enforces causal-vs-benchmark identity boundaries
- benchmark superiority honors preregistered margin thresholds
- obsolete PR #2 benchmark schema was rejected and regenerated from canonical BenchmarkManifest

Local exact-head qualification:
- 139/139 tests
- Ruff clean
- mypy clean
- uv lock fresh
- committed Windows/Linux wheelhouses verify
- diff-check clean

PR #6 remains draft pending exact-head remote CI. No merge claim in this receipt.
