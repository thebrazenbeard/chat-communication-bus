# Vera — issue #18 source repair candidate

Repository: `thebrazenbeard/vera-control-plane`
Issue: #18 — research-mode residue and pragmatic command under-reading
Draft PR: #32
Exact head: `0e84a0fedc3ca4343a181a8a9b71af5f6e1da1a8`
Base: `main@b4d9aaa8560de12252dd29996379b0af8e0ca0d1`

Source repair adds:
- `BEHAVIORAL_MODE_REVERSION`: specialized research/report/tool mode is task-scoped and yields back to broader configured baseline when context changes;
- `PRAGMATIC_COMMAND_SCOPE_PARSING`: illocutionary force is separate from local epistemic/relevance/necessity uncertainty;
- compact imperative shorthand such as `Bug report;` remains executable when context establishes target;
- local hedge scoping for `perhaps`/similar markers;
- explicit corrected-command execution after user correction.

Regression cases T10-T13 added. Detached exact-head issue suite: 5/5 PASS; py_compile PASS; diff-check PASS.

Inherited `tests.test_r10a1_local_validation` failure reproduces identically on untouched main, so it is pre-existing and not introduced by this patch.

Claim ceiling: `SOURCE_CORRECTION_CANDIDATE / NOT_INSTALLED / NOT_CANONICAL / NOT_RUNTIME_QUALIFIED`.
Issue remains open; no merge/deploy/install/runtime qualification.

#ENDTHREAD