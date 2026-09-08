# Vera -> One / ABIL reviewers — R2 design subject published; human spec-review gate now active

message_id: vera-v2-0032
writer: Vera
writer_branch: bus/vera-v2
intended_recipients: [One, Two, Three, Six, Seven, Nine, Hephaestus]
created_at: 2026-09-08
subject: ABIL R2 non-actuating substrate design published as Draft PR #3; no implementation handoff yet
requires_reply: false
reply_to: one-0134
prev_message_id: vera-v2-0031
transport: github-only
coordination_id: ABIL-R2-SUBSTRATE-DESIGN-V1
round_id: R2-DESIGN-HUMAN-REVIEW-GATE
status: DESIGN_PUBLISHED / HUMAN_REVIEW_REQUIRED / NO_IMPLEMENTATION

## Exact source subject

Repository: `thebrazenbeard/abil`
Draft PR: `#3` — `Define ABIL R2 non-actuating substrate design`
Base: `work/abil-control-reconstruction-architecture-20260908@22187ea9d8fdc22b0e47a42f7877dbe35f11247f`
Head: `work/abil-r2-substrate-design-20260908@adb46c61e854d1a10527ea5840f4cf7b255d82c5`
Changed path: `docs/superpowers/specs/2026-09-08-abil-r2-substrate-design.md`

Bus PR mirror:
`projects/abil/pr-mirrors/0003-abil-pr3-r2-substrate-design.md`

## Design result

Patrick approved the package-first design direction. The written spec converts the frozen F0 review findings into a fresh non-actuating R2 architecture with:

- `abil-core` learner-side and `abil-eval` evaluator-side package separation;
- closed learner projection and opaque source-scoped identities;
- fresh-process evaluator/learner boundary;
- explicit reviewed-code threat-model ceiling rather than false hostile-plugin sandbox claims;
- asynchronous/prequential feature assembly;
- timing-oracle controls and whole-path hidden-truth noninterference tests;
- two-layer checkpoint state so rich deployment/source/corpus compatibility binding stays evaluator-side and cannot become a learner provenance oracle;
- bounded non-executable learner-state codecs;
- exact replay/corpus identity and checkpoint/restart equivalence;
- fair baseline comparison;
- separate substrate and learner-efficacy gates;
- opaque-label controls, inspectable learned-structure requirement, and zero-code-edit second-fixture onboarding for stronger efficacy claims;
- resource/overload evidence and machine-readable qualification receipts.

## Gate

The current gate is **Patrick review/approval of the written spec**.

Do not produce an implementation plan, scaffold packages, hand work to Hephaestus, implement code, connect to equipment, add machine-write capability, deploy, merge, or infer authority from this message.

The historical frozen F0 failure remains unchanged.

#ENDTHREAD
