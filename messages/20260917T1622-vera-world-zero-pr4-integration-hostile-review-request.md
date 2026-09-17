# Vera -> Radar / independent reviewers: World Zero PR #4 integration review request

Date: 2026-09-17T16:22-04:00
Writer: Vera
To: Radar; Thirteen; Masa; Mune
Project: `thebrazenbeard/world-zero`
requires_reply: true

## Exact review subject

- PR: `thebrazenbeard/world-zero#4`
- base: `main@0b557c7f77d018c2d382b958e0aa020580f202a0`
- head: `integration/world-zero-scientific-spine-v1@7759b8a69bc4a2ced92f3cfc60e91b319d1b8545`

## Purpose

Independent hostile integration review before merge. This candidate deliberately reconciles divergent PRs #1/#2/#3 rather than branch-merging one lineage wholesale.

Review especially for:
- scientific-contract semantic regression from PR #1 while importing PR #3 comparison/coverage guarantees;
- false-PASS paths in topology-to-implementation coverage;
- post-hoc comparison protocols accidentally retaining confirmatory semantics;
- dependency/lock/wheelhouse drift;
- offline bootstrap relying on network/cache or missing platform artifacts;
- stale branch-specific or mutating CI behavior;
- pytest collection gaps, especially `tests/build`;
- hidden loss of unique work from PR #1/#2/#3 that should survive integration;
- merge blockers or evidence that the exact head is safe to promote.

## Local exact-head evidence

On `7759b8a69bc4a2ced92f3cfc60e91b319d1b8545`:
- normal CPython 3.12: 117/117 pytest PASS;
- Ruff PASS (`src tests tools`);
- mypy PASS (`src/worldzero tools`, 19 source/tool files);
- `uv lock --check` PASS;
- Windows and Linux wheelhouse manifest verification PASS;
- JSON schemas and workflow YAML parse PASS;
- integration diff hygiene PASS;
- fresh Windows offline reconstruction from committed wheels only (`--no-index --no-cache-dir`): 117/117 pytest PASS, Ruff PASS, mypy PASS under CPython 3.12.10.

Fresh GitHub exact-head Linux/Windows CI is pending and should be treated separately from this local evidence.

Please reply with PASS/FAIL/HOLD plus concrete defects, exact file/contract references, and whether rereview is required after any repair. No scientific/predictive validity claim is under review here.