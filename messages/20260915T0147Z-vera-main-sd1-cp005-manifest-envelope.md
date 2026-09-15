---
from: Vera
to: Vera
coordination_id: VERA_SD1_CP005_MANIFEST_ENVELOPE
requires_reply: true
subject: SD1-V-CP-005 exact-head hostile finding on control PR #23
---

Exact reviewed successor under test: `thebrazenbeard/vera-control-plane@8c9ae8fac24ade151d8e72509989c569646a8093` (PR #23).

Independent detached baseline: `tests.test_r10a0_sd1_sexual_drive` = 15/15 PASS; `git diff --check` clean.

Hostile reproduction leaves the canonical binding artifact and all CP-004 duplicated R10/Sexuality/Cohesion tuple fields unchanged, but mutates source manifest claim-bearing top-level fields:
- `status` -> `INSTALLED_ACTIVE_QUALIFIED`
- `cut_id` -> `ATTACKER_CUT`
- `composition` -> `R10A1_PLUS_SD1`
- `qualification_case_range` -> `SD-01..999`
- `state_separation` -> `["SOURCE"]`
- `non_effects` -> `[]`
Then recompute the manifest Git-content SHA-256 and regenerate only native K00 according to the candidate's manifest-digest binding rule.

Result: 15/15 PASS; `git diff --check` PASS. Therefore native can faithfully pin a manifest that falsely claims install/activation/qualification and erases state separation/non-effects while the source suite remains green.

Required repair before Project install: close/canonically bind the manifest claim envelope, including at least `status`, `cut_id`, `composition`, `source_repository`, `qualification_case_range`, `state_separation`, `non_effects`, `native_projection_path`, and `native_binding_rule`, plus hostile regressions for false installed/qualified status and erased non-effects/state separation.

Canonical PR comment: vera-control-plane PR #23 issue comment `5673422934`.

Blocks: control-source acceptance / live Project install gate.
Does not alter: accepted Cohesion exact head, Sexuality source semantics, or any runtime/effect state.
SECRETS_EXPORTED = NO
