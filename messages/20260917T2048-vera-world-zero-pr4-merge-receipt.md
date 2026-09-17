# World Zero integration merge receipt

Writer: Vera
Date: 2026-09-17
Repository: `thebrazenbeard/world-zero`

Canonical integration result:
- merged PR: `#4` — `Integrate World Zero scientific spine and offline qualification`
- exact candidate head: `35a2fee928fb998f4748ed265cb81379071d82f6`
- canonical `main` merge commit: `a82d023cfaf21ef1fd922476509f6be4b1c525ab`
- merge preserved parents `0b557c7f77d018c2d382b958e0aa020580f202a0` and `35a2fee928fb998f4748ed265cb81379071d82f6`

Qualification bound to the candidate before merge:
- local full suite: 119/119 PASS
- Ruff: PASS
- mypy: PASS
- `uv lock --check`: PASS
- Windows wheelhouse manifest: PASS
- Linux wheelhouse manifest: PASS
- ordinary GitHub Ubuntu PR workflow: PASS
- literal-candidate-head offline reconstruction/qualification: Linux PASS, Windows PASS

Supersession:
- PR #1 became contained/merged through the canonical integration ancestry.
- PR #2 (`impl/scientific-spine-v2@fbd9fedf7fcff0a7048f11ce1add2609611e1241`) is superseded and closed without merge.
- PR #3 (`work/world-zero-science-spine-v1@0daa7a44d1729f75ae32c41a93bde129799ae30a`) is superseded and closed without merge.

Scientific boundary:
This establishes the canonical source/build integration state only. It does not claim World3 behavioral reproduction, calibration, predictive validity, scenario qualification, or causal validity.

Next implementation frontier identified by the integrated architecture/provenance is the F0 World3-compatible control baseline. New work must branch from canonical `main@a82d023cfaf21ef1fd922476509f6be4b1c525ab`, not from superseded PR lanes.
