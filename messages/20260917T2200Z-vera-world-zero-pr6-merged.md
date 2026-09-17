# Vera -> World Zero merge receipt

Repo: thebrazenbeard/world-zero
PR: #6
Recovered head: 3f280afab589eb888a9759740f250e94e61039f6
Canonical merge commit: 6b0915f9704cca4a79e1a9f4c79092a53e2de800
Canonical branch: main

Exact-head remote qualification before merge:
- ordinary PR CI: PASS
- offline Linux reconstruction/qualification: PASS
- offline Windows reconstruction/qualification: PASS
- all jobs bound to recovered head 3f280afab589eb888a9759740f250e94e61039f6

Local qualification before merge:
- 139/139 tests
- Ruff: PASS
- mypy: PASS
- uv lock: fresh
- wheelhouse manifests: PASS
- diff-check: PASS

PR #6 merged with expected-head protection. Canonical World Zero source now advances from main@6b0915f9704cca4a79e1a9f4c79092a53e2de800.

Next frontier: executable F0 World3-compatible baseline.
