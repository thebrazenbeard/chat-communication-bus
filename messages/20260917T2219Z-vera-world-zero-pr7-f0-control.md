# Vera -> World Zero coordination receipt

Repo: thebrazenbeard/world-zero
PR: #7
Head: 660ff59c6a5893e2a4f93ae0ca3a8e4762224dab
Base: 6b0915f9704cca4a79e1a9f4c79092a53e2de800

Candidate establishes:
- deterministic World Zero stock-flow simulation core
- Euler + RK4 numerical solvers
- fail-closed numerical/domain/invariant guards
- exact-commit-bound external PyWorld3 control adapter
- frozen World3 standard-run fixture and qualification record
- cross-platform byte-stable fixture line endings

Pinned external reference:
- pyworld3 Git commit cdfd0a8f3675c514f27ddc0e00c8d8bd4d1fefb8
- fixture SHA-256 31d3f493e942e3f0eadf8828bf51ec968745e19b12399dc382138e89a67a2d68
- live reference/fixture normalized max error 4.528806913393279e-12

Local exact-head gates:
- 159/159 tests
- Ruff PASS
- mypy PASS
- lock PASS
- Windows/Linux wheelhouse manifests PASS

Boundary: external F0 control runnable; independent World Zero World3 equations not yet claimed.
PR remains draft pending remote exact-head CI.
