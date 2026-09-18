# Vera -> World Zero coordination receipt

Repo: thebrazenbeard/world-zero
PR: #14
Head: eb4fd75a8a77c98bbfcebb204308d9a716ecc44d
Base: c4a1252bf9979bbca1a0c9ef33097ab5cb376334

Candidate:
- admits exact UN WPP 2024 age5/sex Medium source
- payload SHA a04d7d1486a5eb2832cc812d599448f0a71e8ac9e1e7e6fa4066673d6a2487cd
- freezes WZ_AGE_COHORT_V0:
  child 0-14
  young_adult 15-39
  mature_adult 40-64
  older_adult 65+
- adds strict 237-country / 21-age-group cohort extraction through frozen macroregion mapping
- preserves WPP projection validation firewall

Clean exact-head local gates:
- 255/255 tests
- Ruff PASS
- mypy PASS
- uv lock PASS
- Windows/Linux wheelhouse manifests PASS
- diff-check PASS

Boundary:
Cohort bands are a V0 modeling convention, not empirical truth.
2026 cohort values remain projection bridge data and are not validation evidence.
Final 2023/2026 derived cohort artifacts are the next frontier.
