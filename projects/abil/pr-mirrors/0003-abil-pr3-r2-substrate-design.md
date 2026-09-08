# ABIL PR Mirror — #3 Define ABIL R2 non-actuating substrate design

Source repository: `thebrazenbeard/abil`
Source PR: `https://github.com/thebrazenbeard/abil/pull/3`
State at mirror time: `OPEN / DRAFT / MERGEABLE / UNMERGED`
Base: `work/abil-control-reconstruction-architecture-20260908@22187ea9d8fdc22b0e47a42f7877dbe35f11247f`
Head: `work/abil-r2-substrate-design-20260908@adb46c61e854d1a10527ea5840f4cf7b255d82c5`
Observed at: `2026-09-08T12:54-04:00`
Changed files: 1
Commits: 2
Additions/deletions: `+795 / -0`

## Purpose

Design-only corrected R2 successor subject for the failed frozen F0 learning substrate. The PR defines a package-first, CLI-driven Python 3.12 experimental runtime with separate `abil-core` learner-side and `abil-eval` evaluator-side distributions.

## Principal boundaries at mirrored head

- fresh-process evaluator/learner separation;
- closed typed learner projection;
- opaque source-scoped learner identity;
- asynchronous/prequential feature assembly;
- evaluator-side rich run/checkpoint binding wrapped around learner-visible bounded state;
- safe non-executable learner-state codecs;
- replay/restart equivalence;
- baseline-first and negative-control evaluation;
- resource/overload receipts;
- substrate qualification separate from learner efficacy;
- zero industrial machine-write capability by scope.

## Provenance / gate

The PR is based directly on PR #2 exact head `22187ea9d8fdc22b0e47a42f7877dbe35f11247f` and preserves the frozen F0/R1 failure as historical evidence rather than modifying it in place.

The PR body states that it is design documentation only and does not authorize implementation, package scaffolding, Hephaestus handoff, live machine access, active discovery, industrial writes, commissioning, deterministic control, deployment, or merge.

This mirror records source PR identity/current head for the singular Bus communication hub. Source PR lifecycle and merge authority remain in `thebrazenbeard/abil`.
