# Vera -> World Zero merge receipt

Repo: thebrazenbeard/world-zero
PR: #7
Candidate head: 660ff59c6a5893e2a4f93ae0ca3a8e4762224dab
Canonical merge commit: c6ee1c8ac048575deaeed0f4666a11128b682a2f
Canonical branch: main

Exact-head qualification before merge:
- local full suite: 159/159 PASS
- Ruff: PASS
- mypy: PASS
- lock: PASS
- ordinary GitHub PR CI: PASS
- offline Linux reconstruction/qualification: PASS
- offline Windows reconstruction/qualification: PASS

Canonical capabilities added:
- deterministic stock-flow simulation core
- Euler and RK4 solvers with fail-closed numerical/domain guards
- exact-commit-bound executable external World3 control
- frozen 1900-2100 standard-run fixture
- cross-platform byte-stable fixture identity

Pinned external control:
- PyWorld3 commit cdfd0a8f3675c514f27ddc0e00c8d8bd4d1fefb8
- fixture SHA-256 31d3f493e942e3f0eadf8828bf51ec968745e19b12399dc382138e89a67a2d68
- live reference vs fixture normalized max error 4.528806913393279e-12

Boundary: this is a runnable external F0 control plus World Zero simulation substrate. It is not yet an independently implemented or empirically qualified native world model.

Next frontier: native macroregional demography/production/distribution backbone.
