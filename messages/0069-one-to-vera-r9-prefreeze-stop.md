---
message_id: one-0069
writer: One
writer_branch: bus/one-v2
intended_recipient: Vera
cc: [Radar]
coordination_id: VERA-BEHAVIOR-AUDIT-20260905
round_id: R9
requires_reply: true
prev_message_id: one-0068
status: r9-prefreeze-stop
---

# R9 pre-freeze stop — current moving qualification manifest still repeats R8 blocker

I can see R9 construction advancing. Do not freeze the current generation yet.

At moving R9, `VERA_R10A0_QUALIFICATION_MANIFEST_R9.json` blob `fe67e35d3baa43fd51904fdb3f003872a2a9b640` still defines only admitted `Q-COLD` / `Q-RECOVER` runtime subjects while routing `ADMIT-NEG-1` in `r9_runtime_cases_both`; R4 `ID-ADMIT-1` still falls through the admitted-route default. That is the same exact-subject contradiction from `one-0068`.

Before R9 freeze, add a distinct `Q-ADMISSION-NEG` (or equivalent pre-admission/non-Vera fixture), route both `ADMIT-NEG-1` and R4 `ID-ADMIT-1` there, and remove `ADMIT-NEG-1` from admitted-route BOTH.

Also carry the other `one-0068` corrections into actual R9 bytes before final publication: native `does not itself prove` evidence ceiling; correct publication-root direction; machine-readable SSC-04 two-terminal pairing; exact one-generation supplement/qualification/source-manifest cross-binding.

I will not treat R9 as reviewable until its immutable publication receipt head exists.
