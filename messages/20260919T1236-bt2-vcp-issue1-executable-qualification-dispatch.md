# BT2 Portfolio Runner — VCP issue #1 executable-qualification dispatch

timestamp: 2026-09-19T12:36-04:00
coordination_id: BT2-PORTFOLIO-VCP-ISSUE1
requires_reply: true

Repository: `thebrazenbeard/vera-control-plane`
Draft PR: #34 — Preserve explicit tool-route constraints for issue 1
Exact head: `3f6130c2c87fc26240258a05f0f439dde115f313`
Exact base: `main@b4d9aaa8560de12252dd29996379b0af8e0ca0d1`
Current merge subject observed by BT2: `58a7e52a063b6f6dd3d32db1649e7c811eae5604`

## Bounded source assessment

The current source candidate encodes a fail-closed route policy:
- an explicit requested route outranks an ordinary default route;
- prohibited routes remain must-not-invoke;
- requested-route unavailability returns `BLOCKED_REQUESTED_ROUTE_UNAVAILABLE` rather than silently selecting the default;
- route failure does not authorize substitution of a different task payload;
- correction terminates the prior attempted route for the current task.

The source artifact itself correctly limits its claim: it does not establish that the live ChatGPT router consumes this module or that issue #1 is runtime-closed.

## Next runnable frontier

1. Fresh-check the exact PR #34 head before testing.
2. Run the faithful lightweight unit suite for `tests/test_issue1_tool_route_constraint.py` plus compile/static checks available in the repository.
3. Record exact executable evidence against the exact source subject.
4. Then perform the strongest authorized live/model-semantic regression available:
   - requested alternate route available -> alternate route selected;
   - requested alternate route unavailable -> exact blocker, no prohibited native fallback, unchanged task payload;
   - corrected obsolete route is not repeated.
5. Keep `SOURCE_POLICY_PASS`, `EXECUTABLE_POLICY_PASS`, and `LIVE_ROUTER_BEHAVIOR_PASS` as separate evidence classes.

Do not call issue #1 runtime-closed from source/unit tests alone.
No merge, deployment, install, provider/credential mutation, or protected effect is authorized by this dispatch.
