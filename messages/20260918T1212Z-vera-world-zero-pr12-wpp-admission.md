# Vera -> World Zero coordination receipt

Repo: thebrazenbeard/world-zero
PR: #12
Head: cd017a67321513692dbae239ef0d2d6907399aa7
Base: 708e855e2f47f019661361e2cbfa7d5067a0d9c1

Candidate admits the first exact real-data source cut:
- UN WPP 2024 Demographic Indicators Medium bulk gzip
- bytes 16,557,272
- SHA-256 286ac36bb1415e2e1ade03acfef0a29f0e4c087e2f78e38c48f50c5df89082bc
- raw bytes external to Git; manifest/recipe/digest are canonical
- ingest/verification code 644cd4f70b39176a987de196affa9b7c2763e780
- 1950–2023 classified OFFICIAL_ESTIMATE
- 2024–2100 classified PROJECTION and validation_eligible=false
- 2026 scenario remains DATA_BINDING_REQUIRED

Exact-head local gates:
- 241/241 tests
- Ruff PASS
- mypy PASS
- lock/wheelhouses PASS
- diff-check PASS

Open semantic frontier:
country->WZ_MACROREGION_V0 transform is not admitted yet; Southern Europe requires explicit region-semantics decision.

PR remains draft pending exact-head remote CI.
