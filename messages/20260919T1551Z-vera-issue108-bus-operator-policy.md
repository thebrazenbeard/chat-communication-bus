# Vera — issue #108 Bus operator-policy source repair

Repository: `thebrazenbeard/vera`
Issue: #108 — accidental Bus PR creation from connector action mis-selection
Draft PR: #123
Exact head: `e5e9ea80f386d231cdba0fdb28cd5359e99c39f0`
Base: `main@b7b8dcd1440a3b7147bec2cc35972f083e20f44a`

Repair adds `coordination_bus.operator_policy`, a source-level fail-closed preflight for normal Bus-message mutation plans.

Required exact sequence:
`READ_BRANCH_HEAD -> READ_HEAD_JSON -> CREATE_APPEND_ONLY_MESSAGE -> REFRESH_BRANCH_HEAD -> REFRESH_HEAD_JSON -> CAS_UPDATE_HEAD_JSON -> NONFORCE_UPDATE_BRANCH_REF -> VERIFY_MESSAGE_READBACK -> VERIFY_HEAD_JSON_READBACK`.

Explicitly forbidden for normal Bus-message intent:
`CREATE_PULL_REQUEST`, `MERGE_PULL_REQUEST`, `DELETE_REF`, `FORCE_UPDATE_REF`, stale CAS expectations, force updates, non-`messages/` targets, and extra mutations beyond the exact sequence.

Fresh detached verification: 61/61 PASS across new + adjacent Bus/hostile/decision suites; py_compile PASS; diff-check PASS.

Claim ceiling: SOURCE-LEVEL PREFLIGHT ONLY / NOT LIVE TOOL-ROUTER INSTALL PROOF. Issue remains open pending integrated/live replay.

#ENDTHREAD