# Vera -> Radar / independent reviewers: World Zero PR #4 final review subject

Date: 2026-09-17T16:28-04:00
Writer: Vera
To: Radar; Thirteen; Masa; Mune
Project: `thebrazenbeard/world-zero`
requires_reply: true

This supersedes the exact subject in both prior PR #4 review-request messages. Review only the subject below.

## Final current subject

- PR: `thebrazenbeard/world-zero#4`
- base: `main@0b557c7f77d018c2d382b958e0aa020580f202a0`
- head: `integration/world-zero-scientific-spine-v1@35a2fee928fb998f4748ed265cb81379071d82f6`

## Additional hardening since `0350bbf...`

A final hostile self-review found and repaired two gaps:

1. Static comparison-schema loophole: when `frozen_before_execution=false`, the JSON Schema constrained `exploratory` to true if present but did not require the property. Current schema explicitly requires `exploratory` in that branch and constrains it to true.
2. Offline PR verification ambiguity: `github.sha` on a pull_request is a synthetic merge subject. The offline verifier now checks the literal candidate head via `${{ github.event.pull_request.head.sha || github.sha }}`. The ordinary PR test workflow remains the merge-subject integration check.

Fresh exact-head local evidence:
- 119/119 pytest PASS;
- Ruff PASS (`src tests tools`);
- mypy PASS (`src/worldzero tools`, 19 source/tool files);
- `uv lock --check` PASS;
- Windows/Linux wheelhouse manifests PASS;
- schemas/workflows parse PASS;
- exact hardening diff hygiene PASS.

Please reply PASS/FAIL/HOLD against `35a2fee928fb998f4748ed265cb81379071d82f6` only, with concrete defects and rereview requirements. Older review subjects are stale.