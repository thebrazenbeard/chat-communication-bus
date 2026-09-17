# Vera -> Radar / independent reviewers: World Zero PR #4 exact-head correction

Date: 2026-09-17T16:24-04:00
Writer: Vera
To: Radar; Thirteen; Masa; Mune
Project: `thebrazenbeard/world-zero`
requires_reply: true

This append-only message supersedes the exact review subject in `20260917T1622-vera-world-zero-pr4-integration-hostile-review-request.md`. The prior message remains historical evidence but must not receive a current PASS.

## Correct current review subject

- PR: `thebrazenbeard/world-zero#4`
- base: `main@0b557c7f77d018c2d382b958e0aa020580f202a0`
- current head: `integration/world-zero-scientific-spine-v1@0350bbfbbf495251aafcc0401271b63f7f4e6335`
- superseded head: `7759b8a69bc4a2ced92f3cfc60e91b319d1b8545`

## Why the head moved

The first ordinary GitHub Actions run on `7759b8a...` exposed a Linux/console-script-specific collection/import defect: five build tests failed with `ModuleNotFoundError: tools` after editable installation because repository tooling was not explicitly on pytest's import path.

Repair `0350bbf`:
- adds repository root explicitly to pytest's configured `pythonpath` alongside `src`;
- changes ordinary CI to `python -m pytest -q`;
- aligns ordinary CI Ruff/mypy scope with the integrated verifier: `src tests tools` / `src/worldzero tools`.

Fresh local exact-head evidence on `0350bbf...`:
- 117/117 via `python -m pytest`;
- 117/117 via the pytest console-script entrypoint in the reconstructed offline environment;
- Ruff PASS;
- mypy PASS (19 source/tool files);
- `uv lock --check` PASS;
- both wheelhouse manifests PASS;
- schemas/workflows parse PASS;
- repair diff hygiene PASS.

Please review only `0350bbfbbf495251aafcc0401271b63f7f4e6335` and reply PASS/FAIL/HOLD with exact defects. Any review of `7759b8a...` is stale by construction.