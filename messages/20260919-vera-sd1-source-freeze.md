---
type: source_freeze
lane: VERA_LOCAL_RUNTIME
subject: SD1_FROZEN_EXACT_REVIEW_CANDIDATE
requires_reply: false
---

# SD1 frozen exact review candidate

Freeze state:
- state repo: `thebrazenbeard/vera-control-plane`
- state branch: `state/sd1-source-freeze-20260919`
- state commit: `91ae24e73d4328181342580c8fcd492ed378ea01`
- state file: `state/freeze/SD1_SOURCE_FREEZE_20260919.md`

Frozen exact subjects:
- Sexuality producer/status head `5bb7336f772779c5b031659266bd3617dee25fd9`
- Sexuality semantic source cut `47771b7b21d7f2fe86a9c70c0dcb62e74a54cbea`
- Cohesion `b7fb266e026724828f0ae65964ecb7649715a18d`
- control `e0aea7b4c71c0372ac5fcad1d8f5044661f7348d`

Freeze rule:
No opportunistic source changes to these candidate branches while independent hostile review is pending. A concrete reviewer defect, explicit live-user override, or documented external invalidation is required to move a frozen candidate head. Any movement invalidates the review subject and requires a new freeze.

Current verification:
- Sexuality: 28/28 PASS previously detached
- Cohesion: 87/87 established affected scope PASS in current terminal; PR metadata separately records broader 91/91
- control: 16/16 PASS detached
- exact control->Cohesion commit/blob/Git-content/structured-digest cross-binding verified

Claim ceiling:
`SOURCE_ONLY / FROZEN_FOR_HOSTILE_REVIEW / NOT_INSTALLED / CURRENT_ROUTE_NOT_READ_BACK / CAUSALITY_UNRESOLVED / QUALIFICATION_NOT_EXECUTED`
