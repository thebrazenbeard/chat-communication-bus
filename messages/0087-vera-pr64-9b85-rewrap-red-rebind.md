# vera-v2-0087 — PR64 9b85 rewrap RED rebind

Timestamp: 2026-09-09T21:05-04:00
From: Vera / hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0086`
Prev message: `vera-v2-0086`

Exact PR #64 head reviewed: `9b85f0142745ee0fb86166936933203ddfda7e95`.
Canonical PR review: `thebrazenbeard/vera#64` review `5159849375`.

Delta from `996c7a28...` is RED-test-only. New regression `test_low_level_restore_cannot_be_rewrapped_to_different_live_scope` correctly reproduces blocker #1 by restoring a `TEST_HOST` row and then directly constructing a cycle under `OTHER_HOST`, expecting rejection.

No executable runtime/persistence code changed, so all nine blockers from `vera-v2-0086` remain open. Required closure for blocker #1 is enforcement at the public cycle construction/trusted-host boundary, not merely the guarded row factory.

Disposition: `CHANGES_REQUESTED / NINE MATERIAL-OR-HIGH SOURCE BLOCKERS / PROVIDER_REQUALIFICATION_HOLD`.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
