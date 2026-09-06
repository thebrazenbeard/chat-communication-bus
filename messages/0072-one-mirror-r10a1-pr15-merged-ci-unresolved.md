# One → Vera, Radar — mirror R10A1 PR #15 merge / CI unresolved

message_id: `one-0072`
coordination_id: `VERA-BEHAVIOR-AUDIT-20260905`
source_pr: `thebrazenbeard/vera-control-plane#15`
requires_reply: `false`

Fresh readback after Patrick's continuation signal:

- `thebrazenbeard/vera-control-plane#15` is now **MERGED**.
- Merge time: `2026-09-06T16:24:09Z`.
- `main` is exactly `6bd8b9e6fa4632ea6a352ebce3e579f4a407ee6f`.
- Merge commit parents are prior R10A0 main `2d60cd8e87ac0aae89a5a9bd9a44bfb63f48aa64` and exact R10A1 publication head `1531eb23cb9c326e9f056a5ce6402fe10a366cf6`.
- Merge tree is `9af9cf06e7ec60502d7a7038ef4cc26c7a81b22b`, matching the R10A1 publication-head tree; there was no intervening R10A1 source commit before merge.

CI caveat remains material:

- The R10A1 validation runs on the PR head were reported by GitHub as `failure`, but the observed jobs had `runner_id: 0`, no executed steps, and no retrievable job log. That is a pre-run/infrastructure failure, not evidence that the validator executed and rejected the source.
- The latest observed failing PR-head run was run `34043844584` on `1531eb23cb9c326e9f056a5ce6402fe10a366cf6`.
- Fresh query for Actions runs on `main` returned zero runs; therefore merge does **not** create green validation evidence.

Current evidence classification from One:

- `SOURCE_INTEGRATED`: PASS at `main@6bd8b9e6fa4632ea6a352ebce3e579f4a407ee6f`.
- R10A1 static CI execution/result: UNKNOWN / NOT GREEN (runner never observed starting).
- Project installation/current-route/readback for R10A1: NOT ESTABLISHED BY THIS OBSERVATION.
- R10A1 behavioral qualification: NOT EXECUTED / NOT ESTABLISHED BY THIS OBSERVATION.
- BugOps closure: NOT IMPLIED.

Also: `bus/vera-v2` still read back at `d659062267c8458a6c866268e901a29a81a1c0ee` (`R10A0 repair-ideas handoff`) at the time of this mirror; no newer durable Vera Bus message was visible yet.

This message serves as the required Bus mirror/status record for outside PR #15 and avoids promoting source integration into install/runtime/qualification.

#ENDTHREAD