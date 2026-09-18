# Vera -> World Zero coordination receipt

Repo: thebrazenbeard/world-zero
PR: #9
Head: f32a942fd5017b62dfacb8a21e6f234a8727fec0
Base: 71600c6b1489689bf65814de1744fb0f11b8fd53

Candidate integrates environment feedback into the native shared solver:
- fossil dispatch -> emissions -> climate carbon/temperature
- climate damage -> real output
- soil degradation/recovery -> food output
- water shortage/stress exposure
- land and managed-input food response

Local exact-head gates:
- 203/203 tests
- Ruff PASS
- mypy PASS
- uv lock PASS
- Windows/Linux wheelhouse manifests PASS
- diff-check PASS

Boundary: integrated mechanics only; uncalibrated and not a forecast.
PR remains draft pending exact-head remote CI.
