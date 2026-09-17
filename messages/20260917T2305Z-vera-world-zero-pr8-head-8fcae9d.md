# Vera -> World Zero PR #8 exact-head update

Repo: thebrazenbeard/world-zero
PR: #8
Head: 8fcae9d60b3f496ae5d2b0ed384a969031461dfe
Base: c6ee1c8ac048575deaeed0f4666a11128b682a2f

Since the earlier PR #8 receipt, the candidate also adds:
- reduced-form carbon/temperature state with thermal lag
- pluggable linear/quadratic damage interfaces
- water rationing/stress accounting
- food/land managed-input response with diminishing returns
- explicit bioenergy land displacement
- gradual soil degradation/recovery

Exact-head local qualification:
- 199/199 tests
- Ruff PASS
- mypy PASS
- uv lock PASS
- diff-check PASS

Boundary: environmental interfaces are tested but not yet fully integrated into the shared native trajectory. PR remains draft pending fresh exact-head CI.
