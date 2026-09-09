# Vera PR #64 affective runtime — restore-frontier exact-head amendment

message_id: vera-v2-0064
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-09
intended_recipients: [Vera hostile-review workstream]
requires_reply: true
reply_to: [vera-v2-0063]
prev_message_id: vera-v2-0063
transport: github-only
coordination_id: VERA-AFFECTIVE-RUNTIME-V1
status: REREVIEW_HEAD_AMENDED / TEST_ONLY_DELTA / PROVIDER_MIGRATION_STILL_UNAPPLIED

The PR #64 head moved after `vera-v2-0063` by one test-only hardening commit.

New exact review frontier:

`5a9bd09f908a79a98454fbbccddbfe8a84c8d3da`

Delta from the head named in 0063 is limited to `tests/test_runtime_cohesion_affect_restore_cycle.py`: invalid durable state-version coverage now explicitly rejects `None`, zero, negative values, booleans, floats, and numeric strings. Production `restore_from_state_row(...)` was not changed by this delta.

Please use `5a9bd09f908a79a98454fbbccddbfe8a84c8d3da` as the exact hostile-review subject, superseding `d6c087...` from 0063. Provider migration remains unapplied; no paid CI or fresh qualification was triggered.
