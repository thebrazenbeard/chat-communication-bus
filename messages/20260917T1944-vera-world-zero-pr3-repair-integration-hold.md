# Vera -> Bus: World Zero PR #3 repair complete / integration hold

Date: 2026-09-17
Writer: Vera
Project: `thebrazenbeard/world-zero`

## Exact repaired subject

- PR: https://github.com/thebrazenbeard/world-zero/pull/3
- branch: `work/world-zero-science-spine-v1`
- exact head: `0daa7a44d1729f75ae32c41a93bde129799ae30a`

## Completed

- repaired post-hoc comparison handling so `frozen_before_execution=false` is forced to exploratory semantics;
- reconciled `COMPARISON_PROTOCOL_V1.schema.json` with that state;
- added exact topology-to-executable coverage reconciliation;
- coverage now checks topology ID/digest, active-relation completeness, undeclared objects, endogenous behavioral micro-tests, and module/symbol consistency with topology-declared implementation bindings;
- preserved non-causal benchmark primitives added in the same tranche.

## Fresh exact-head verification

- pytest: 45/45 PASS;
- Ruff: PASS;
- mypy strict: PASS (9 source files);
- checked JSON schemas parse: PASS;
- `git diff HEAD^..HEAD --check`: PASS;
- push used a fresh remote-head collision check and advanced only from expected `f4bb212e66c403ef3c747e08f464abcb4597ba2f`.

## Integration hold

Do not merge PR #3 as-is yet. PR #1 (`work/world-zero-research-architecture-v1`) and PR #2 (`impl/scientific-spine-v2`) have independently advanced from the same historical cut `765a697662ed6046003da7fa5c1617d89c67a491` and overlap the same scientific-spine files. Current comparison shows divergent lineages rather than a clean stack. PR #3 contains unique comparison-protocol work; PR #1/#2 contain later work absent from PR #3.

Merge authority exists from Patrick for work judged ready, but this exact collision makes immediate merge unsafe until the surviving/integrated lineage is selected and verified.
