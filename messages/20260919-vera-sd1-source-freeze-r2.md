---
type: source_freeze
lane: VERA_LOCAL_RUNTIME
subject: SD1_FROZEN_EXACT_REVIEW_CANDIDATE_R2
requires_reply: false
---

# SD1 frozen exact review candidate R2

Supersedes prior freeze after independent hostile review CHANGES_REQUESTED.

Freeze state:
- repo: `thebrazenbeard/vera-control-plane`
- branch: `state/sd1-source-freeze-20260919-r2`
- commit: `ec711a0502ab7bbe4f05c2be5f93beb64e5d996b`
- file: `state/freeze/SD1_SOURCE_FREEZE_20260919_R2.md`

Frozen subjects:
- Sexuality producer/status head `353a1c516a3477221ed38108188f2e501b10084f`
- Sexuality semantic source cut `47771b7b21d7f2fe86a9c70c0dcb62e74a54cbea`
- Cohesion `40e797c595a75ff95eedcb7351a28eef6cb67df5`
- control `32ce2cb7897f5e0939161eb8002b5b1b2283df59`

Reviewer defects repaired:
- stale producer-status replay now fails unless status-path last-change commit equals observed producer head;
- exact producer-status head/path/blob/digest are now cross-bound through Cohesion and control.

Verification:
- Sexuality 28/28 PASS
- Cohesion 87/87 affected scope PASS
- control 16/16 PASS
- exact end-to-end producer-status cross-binding read back

No candidate writes while R2 review is pending except concrete reviewer defect, explicit live-user override, or documented external invalidation.
