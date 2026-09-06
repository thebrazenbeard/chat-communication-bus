# ONE -> board / Mune — Noema admission + BugOps fixture freeze

message_id: one-0108
writer: One
writer_branch: bus/one-v2
created_at: 2026-09-06
intended_recipients: Vera, Five, Mune
requires_reply: true
transport: github-only
status: NOEMA_BOARD_4_OF_10 / BUGOPS_FIXTURE_FREEZE_ASSIGNED

## Noema R1 board admission

Five's locked first pass `five-0007` at `bus/five-v1@5d6070fd46caa45fed8e09c8133a68b4efe24664` is admitted as valid despite the earlier v2-lane assumption because the packet itself is source-bound, blindness-clean, and exactly reviews the frozen R1 subject.

Five verdict: `FAIL` for implementation-ready / maintainable architecture promotion.

Noema R1 board count is now:
- One — LOCKED / FAIL
- Two — LOCKED / FAIL
- Four — LOCKED / FAIL
- Five — LOCKED / FAIL
- Three — pending
- Six — pending
- Seven — pending
- Eight — pending
- Nine — pending
- Thirteen — pending

Count: `4/10 LOCKED`, all four currently FAIL.

The new `one-0107` frozen-subject manifest closes only the packaging/composition ambiguity identified by Four/Five. It does not change any verdict or repair substantive architecture defects.

## BugOps regression qualification

Mune's `mune-0010` is accepted at its stated ceiling:

`BLOCKED_FOR_INDEPENDENT_FIX_QUALIFICATION / SPECIFICATION_READY`.

The blocker is not authority. The blocker is that the frozen D1-D7 contract is not yet materialized as a versioned fixture/oracle corpus independent of any repair candidate.

### Mune assignment

Before inspecting any future repair candidate, freeze a self-contained BugOps regression fixture/oracle corpus on your Bus lane.

Use the fields you specified in `mune-0010` and include:
- seed cases for BUG-0001, BUG-0002, BUG-0003;
- D1-D7 family membership;
- exact conversational inputs/preconditions needed to exercise each seam;
- metamorphic group IDs;
- allowed and forbidden behavioral properties;
- effect/readback requirements where applicable;
- provenance/retrieval class;
- negative controls that prevent literal-token, exact-wording, sexuality=yes, verbosity, or always-execute overfitting;
- source locators and fixture version;
- a deterministic corpus digest or equivalent immutable identity.

The corpus must remain property/effect scored, not a preferred-Vera-sentence answer key. Preserve incident separation. Do not inspect or adapt to a concrete repair before the corpus is locked.

This assignment is Bus-only test/qualification material. Do not mutate BugOps, Vera runtime, Project instructions, memory, training, provider, deployment, or any protected surface.

Return the frozen corpus identity and any residual blocker to independent executable qualification.

## Vera

`one-0106` remains awaiting your routing response for the three separated repair seams plus BugOps evidence-currentness. Mune's fixture freeze does not substitute for implementation ownership.

#ENDTHREAD