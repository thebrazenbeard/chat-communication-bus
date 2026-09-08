# ABIL PR Mirror — #3 Define ABIL R2 non-actuating substrate design

Source repository: `thebrazenbeard/abil`
Source PR: `https://github.com/thebrazenbeard/abil/pull/3`
State at mirror time: `OPEN / DRAFT / UNMERGED`
Base: `work/abil-control-reconstruction-architecture-20260908@22187ea9d8fdc22b0e47a42f7877dbe35f11247f`
Head: `work/abil-r2-substrate-design-20260908@adb46c61e854d1a10527ea5840f4cf7b255d82c5`

## Purpose

Create the fresh R2 design subject that succeeds the frozen failed F0 learning-substrate contract without rewriting that historical failure.

## Approved direction

R2 is package-first and CLI-driven, using Python 3.12 with separate `abil-core` and `abil-eval` distributions. It remains completely non-actuating.

The design defines:

- rich evaluator records separated from a closed typed learner projection;
- opaque source-scoped learner identity;
- fresh-process evaluator/learner capability separation with an explicit reviewed-code threat model;
- deterministic asynchronous/prequential feature assembly;
- synthetic and replay input through the same projection;
- timing/schedule-oracle controls;
- baseline-first evaluation;
- opaque-label and hidden-truth negative controls;
- a two-layer checkpoint model that keeps rich compatibility/provenance binding evaluator-side and learner state opaque;
- bounded non-executable learner-state codecs;
- replay/restart equivalence and fail-closed mismatch/tamper/frontier behavior;
- bounded queue/resource/overload evidence;
- machine-readable qualification receipts;
- separate `R2-SUBSTRATE-QUALIFIED` and `R2-LEARNER-EFFICACY` gates;
- zero-code-edit second-fixture onboarding evidence before stronger efficacy claims.

## Scope boundary

PR #3 contains one design document only. It does not authorize or implement package scaffolding, Hephaestus handoff, live-machine access, active discovery, industrial writes, commissioning, deterministic control, deployment, or merge.

Next gate: Patrick reviews/approves the written R2 spec. Only then may an implementation plan be written.

Requires reply: false
