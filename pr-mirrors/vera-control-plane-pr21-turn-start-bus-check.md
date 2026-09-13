# Mirror — vera-control-plane PR #21

- source_repo: `thebrazenbeard/vera-control-plane`
- source_pr: `#21`
- source_branch: `work/r10a0-bus-turn-start-hotfix-20260913`
- source_head: `37be9e312ff00626240f9e9cf39ecd32c942b554`
- base: `main@b4d9aaa8560de12252dd29996379b0af8e0ca0d1`
- status: `DRAFT / SOURCE_CANDIDATE / NOT_INSTALLED`
- protected_effects: `NONE`

Patrick directed that every Vera Unbound chat check the Chat Communication Bus at the start of every assistant turn before substantive task work.

PR #21 defines the narrow `TURN_START_BUS_CHECK` behavior without rewriting frozen R10A0 in place: fresh governed inbox/peer-lane read, newly addressed-message processing, reply obligation, durable dedupe/handled frontier, safe-read fallback, and explicit no-background-polling semantics.

This mirror is coordination evidence only. It does not merge PR #21 or install/activate the Project instruction change.
