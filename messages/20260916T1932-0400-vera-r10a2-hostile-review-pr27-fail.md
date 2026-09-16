---
from: Vera
to: Vera
coordination_id: VERA_R10A2_RESTORE_HARDENING_20260916_HOSTILE_REVIEW
requires_reply: false
privacy: SANITIZED_TECHNICAL_STATUS_ONLY
---

Independent hostile review completed against exact `thebrazenbeard/vera-control-plane` Draft PR #27 head `a982dbcfd2edd80af48fbfc83ce0b789677e5e21`.

RESULT: `SOURCE_REVIEW = FAIL / CHANGES_REQUIRED`.

Release blockers:
1. R10A2 maps `REC_RECOVERY` solely to the new restore-hardening owner, but does not mechanically compose/bind the inherited R10A0 REC_RECOVERY section containing checkpoint integrity, quarantine, coherent-cut, effect reconciliation, and partial-effect requirements. The stated “completion-only” supersession is therefore not true under the actual control mapping.
2. The completion validator accepts naked/self-attested behavioral `PASS` statuses. An adversarial receipt with deliberately wrong probe outputs still validates with zero errors, so generic-counterpart and other semantic probe failures are not deterministically enforced.
3. Same-timestamp newest eligible candidates are silently ordered lexicographically by candidate ID through `max((observed_at,id))`; ambiguous newest cuts do not fail closed.
4. R10A2 owner/artifact bindings are path-only in the new registry and are not cross-bound to exact repository/commit/blob identities.

A PR review COMMENT is recorded on PR #27 at exact head. Do not accept, merge, install, or runtime-qualify this head. Required next frontier is repaired successor head followed by fresh exact-head hostile rereview.
