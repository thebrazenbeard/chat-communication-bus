# Vera — control-plane issue #1 explicit tool-route source repair

Repository: `thebrazenbeard/vera-control-plane`
Issue: #1
Draft PR: #34
Exact head: `3f6130c2c87fc26240258a05f0f439dde115f313`
Base: `main@b4d9aaa8560de12252dd29996379b0af8e0ca0d1`

Repair: explicit requested route outranks defaults; prohibited routes survive correction; corrected obsolete route is terminated; unavailable requested route blocks instead of silently falling back; original task payload is preserved rather than substituted.

Fresh detached evidence: 10/10 PASS; py_compile PASS; diff-check PASS.

Inherited R10A1 validator failure is predecessor-identical and not introduced by this branch.

Claim ceiling: SOURCE ROUTE POLICY ONLY / NOT LIVE TOOL-ROUTER INSTALL OR QUALIFICATION.
Issue remains open pending live/model-semantic replay.

#ENDTHREAD