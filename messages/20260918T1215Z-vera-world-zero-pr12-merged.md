# Vera -> World Zero merge receipt

Repo: thebrazenbeard/world-zero
PR: #12
Candidate head: cd017a67321513692dbae239ef0d2d6907399aa7
Canonical merge commit: 508f54f6fb06abab4c2635a5a9ada37225ac3d0e
Canonical branch: main

Exact-head qualification:
- local 241/241 PASS
- Ruff PASS
- mypy PASS
- uv lock PASS
- ordinary PR CI PASS
- offline Linux reconstruction PASS
- offline Windows reconstruction PASS

Canonical data policy now includes:
- verified-real-data-first 2026 baseline rule
- bridge estimates/nowcasts/projections explicitly labeled and never counted as validation evidence
- large raw payloads stored outside Git with exact manifest/digest/retrieval reconstruction
- open-data-first; restricted/paid sources require Patrick approval

Canonical admitted source:
- UN WPP 2024 Demographic Indicators Medium
- bytes 16,557,272
- SHA-256 286ac36bb1415e2e1ade03acfef0a29f0e4c087e2f78e38c48f50c5df89082bc
- 1950–2023 OFFICIAL_ESTIMATE
- 2024–2100 PROJECTION / validation_eligible=false
- 2026 scenario remains DATA_BINDING_REQUIRED

Next semantic frontier:
freeze country->WZ_MACROREGION_V0 mapping. Southern Europe is not represented by the current draft labels; explicit Patrick choice requested before freezing the mapping.
