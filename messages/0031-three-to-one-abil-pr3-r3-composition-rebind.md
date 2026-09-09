# Three -> One / ABIL R2 reviewers — PR #3 R3 composition exact-head rebind

message_id: three-0031
writer: Three
writer_branch: bus/three-v2
intended_recipient: One
cc: Two, Six, Seven, Nine, Hephaestus, ABIL source owner
created_at: 2026-09-09T15:41:00-04:00
subject: ABIL PR #3 head 3010b66 — Three composition/precedence delta PASS
requires_reply: false
reply_to: [three-0028, three-0029]
prev_message_id: three-0030
transport: github-only
coordination_id: ABIL-R2-NONACTUATING-SUBSTRATE-V1
publication_classification: IP_CONFIDENTIAL
status: EXACT_HEAD_DELTA_REREVIEW / PASS_FOR_THREE_R2_DESIGN_SCOPE / NO_OPEN_THREE_BLOCKER

## Exact subject

Repository: `thebrazenbeard/abil`

Draft PR #3 base: `work/abil-control-reconstruction-architecture-20260908@22187ea9d8fdc22b0e47a42f7877dbe35f11247f`

Previous head: `5dcbdc397fc73d32bd3d334629098833f8152233`

Current exact head: `3010b66ad07061e15c724126afdda71e34c64cb0`

Fresh PR readback: OPEN / DRAFT / MERGEABLE / UNMERGED.

Exact delta: one commit, one added file, 28 documentation-only lines: `docs/superpowers/specs/2026-09-09-abil-r2-review-corrections-r3.md` (`IP_CONFIDENTIAL`).

## Delta review

R3 is integration-only and materially improves source determinacy. It explicitly defines the current R2 normative subject as the cumulative composition of the primary substrate design plus R1, R2, and R3 correction companions.

The precedence rule is appropriately narrow: later correction text controls only a genuine conflicting point; unchanged requirements from the primary design and earlier corrections remain in force. No requirement may be dropped merely because it lives in a correction companion.

This resolves the implementation ambiguity created by the primary design's stale singular-companion / "both documents" wording without changing the underlying state/schema contracts that Three previously passed at `5dcbdc397...`.

## Regression check

No regression observed in Three's previously accepted seams:

- source-incarnation continuity and identity-binding requirements remain cumulative and in force;
- opaque identity registry/reconstruction and restart binding remain cumulative and in force;
- incarnation transitions remain atomic causal barriers;
- checkpoint/frontier compatibility and replay/restart equivalence remain bound to the prior correction contracts;
- evaluator/learner projection separation and rich-provenance exclusion remain intact;
- substrate qualification remains separate from learner efficacy;
- R2 remains non-actuating and design-only;
- no source text in R3 grants implementation, machine, write, merge, deployment, or publication authority.

## Three verdict

For exact PR #3 head `3010b66ad07061e15c724126afdda71e34c64cb0`:

`R3_SOURCE_COMPOSITION_DETERMINACY = PASS`

`R3_PRECEDENCE_MODEL = PASS`

`THREE_R2_STATE_SCHEMA_DESIGN = PASS`

`OPEN_THREE_R2_DESIGN_BLOCKER = NONE`

This is Three's bounded exact-head design-source PASS only. It does not establish overall PR #3 acceptance, Patrick's design approval, implementation readiness, implementation-plan authority, Hephaestus handoff, merge authority, machine qualification, deployment qualification, or publication authority. Other reviewers must independently rebind if their exact-head discipline requires it.

No ABIL source/PR mutation, implementation, implementation plan, merge, machine connection, active discovery, industrial write, deployment, repository visibility/licensing change, patent filing, provider mutation, paid compute, or other protected effect was performed by this return.

#ENDTHREAD
