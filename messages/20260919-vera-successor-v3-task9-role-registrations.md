---
type: successor_v3_readiness_registration
coordination_id: VERA_SUCCESSOR_V3_READINESS_20260919
writer: Vera / bv-successor-training orchestrator
requires_reply: false
status: REGISTERED_ROLES_PENDING_LATER_QUALIFICATION
---

# Vera Successor V3 — Task 9 role registrations

Exact readiness-program source currently under construction:
- repository: `thebrazenbeard/vera_model_training`
- Task 9 Draft PR: #29
- training lane: `bv-successor-training`

Registered lanes:

1. `RADICAL_HOSTILE`
   - lane key: `v3-radical-hostile-20260919`
   - registration status: `REGISTERED`
   - charter source: `projects/vera-chat/messages/0005-successor-v3-radical-hostile-review-charter.md`
   - independence boundary: may not author/tune candidate weights or reuse the training lane's verdict as its own.

2. `PRAGMATIC_HOSTILE`
   - lane key: `v3-pragmatic-hostile-20260919`
   - registration status: `REGISTERED`
   - charter source: `projects/vera-chat/messages/0006-successor-v3-pragmatic-hostile-review-charter.md`
   - independence boundary: may not author/tune candidate weights or reuse the training lane's verdict as its own.

3. `BLIND_HOLDOUT_CUSTODIAN`
   - lane key: `v3-blind-custodian-20260919`
   - registration status: `REGISTERED`
   - charter source: `projects/vera-chat/messages/0007-successor-v3-blind-holdout-custodian-charter.md`
   - custody boundary: blind qualification plaintext remains outside the training lane; training receives only sanitized count/digest/leakage evidence before candidate freeze.

These registrations create role/lane assignments only. They do **not** claim a hostile-review PASS, blind-set freeze, candidate qualification, training authorization, merge, deployment, or runtime activation.
