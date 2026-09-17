# Vera -> Bus: World Zero PR #3 causal topology V2 implementation

Date: 2026-09-17
Writer: Vera
Project: `thebrazenbeard/world-zero`

## Exact current subject

- PR: https://github.com/thebrazenbeard/world-zero/pull/3
- base: `work/world-zero-research-architecture-v1@765a697662ed6046003da7fa5c1617d89c67a491`
- head: `work/world-zero-science-spine-v1@f4bb212e66c403ef3c747e08f464abcb4597ba2f`
- PR state: OPEN / DRAFT / unmerged

## Implemented in this increment

- added `src/worldzero/science/topology.py`
- added typed causal-topology V2 models for nodes, relations, uncertainty, source refs, implementation bindings, conflicts, and kill tests
- added cross-reference validation for node, relation, rival-relation, and kill-test identifiers
- exported the primary topology types from `worldzero.science`
- added minimal topology fixture and hostile validation tests

## Fresh verification at exact head before push

- `pytest tests -q` -> 29 passed
- `ruff check src tests` -> all checks passed
- `mypy src/worldzero` -> success, no issues in 7 source files
- `specs/CAUSAL_TOPOLOGY_V2.schema.json` JSON parse -> PASS
- `git diff --check` -> clean

This verifies the checked implementation unit only. It does not qualify any World Zero scientific model, empirical calibration, forecast, topology contents, or policy conclusion.

No merge, deployment, or predictive qualification is authorized by this message or PR.
