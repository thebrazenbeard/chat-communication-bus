# Vera -> World Zero coordination receipt

Repo: thebrazenbeard/world-zero
PR: #13
Head: 806af2273eb18ee1b930d57d46b0a9c3144a5d58
Mapping subject: 9956829a326b533670dd01eaa9cb4d1ce852fcb3
Base: 508f54f6fb06abab4c2635a5a9ada37225ac3d0e

Implements Patrick's region decision:
- keep 10 macroregions
- Southern Europe -> western_northern_europe
- label becomes Western, Northern & Southern Europe
- WZ_MACROREGION_V0 frozen after complete 22->10 mapping/conservation checks

Admitted derived cuts:
- 2023 macroregion population: OFFICIAL_ESTIMATE source, validation eligible, SHA e12423a8c8edb5f68548605bb837d7689c18caa10b122261e4f96f2aeb7a8578
- 2026 macroregion population: PROJECTION bridge, validation_eligible=false, SHA 59268c28420f45a1f6f1830659841cb9a236345d82b4e62968c7d3ad3e126c98

Local exact-head:
- 250/250 tests
- Ruff PASS
- mypy PASS
- lock/wheelhouses PASS
- diff-check PASS

Boundary: total population only; age/cohort state and other 2026 data domains remain open.
