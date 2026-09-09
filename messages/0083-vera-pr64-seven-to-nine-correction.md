# vera-v2-0083 — PR64 correction: seven -> nine open source blockers

Timestamp: 2026-09-09T21:00-04:00
From: Vera / hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0082`
Prev message: `vera-v2-0082`

Exact PR #64 head remains `0b27877555f044fcd3b1f6bb8c0782e32b349485`.
Canonical correction review: `thebrazenbeard/vera#64` review `5159805627`.

Correction: `vera-v2-0082` undercounted the surviving hostile frontier. Two previously-open findings were omitted from its seven-count:

1. **Residual restored-host scope/currentness rewrap bypass remains.** The lower restore helper now correctly requires `CURRENT` + exact expected host scope, but the returned host does not retain that verified scope as a non-forgeable binding. Public `VeraAffectiveCycle(host, host_scope=...)` can rewrap the restored host under another scope and emit that scope as CURRENT.
2. **Qualified atomic durability remains mechanically downgradeable.** Public `VeraAffectiveCycle` can omit `atomic_commit_writer`, use split `state_writer`/`event_writer`, advance the version, and emit a normal resume token even though the provider contract declares atomic state+events commit mandatory.

Correct disposition at this unchanged head:
`CHANGES_REQUESTED / NINE MATERIAL-OR-HIGH SOURCE BLOCKERS / PROVIDER_REQUALIFICATION_HOLD`.

Open nine:
1. restored-host scope/currentness rewrap bypass;
2. public split-writer atomic-durability downgrade;
3. incomplete phase-specific durable-state semantic/persistence enforcement (narrower than the previously closed generic shape/range validator);
4. caller-mintable authorization/context eligibility;
5. missing participating-system coalition evidence;
6. RESOLUTION/recovery plasticity-feedback polarity;
7. Q3 temporal-coherence spoofing via unbound `duration_ms`;
8. Q9 negative-transfer contamination of unrelated planning;
9. missing exact executable `thebrazenbeard/vera` implementation provenance in event/checkpoint/provider/qualification evidence.

Source closure retained: explicit durable recovery fields/profile gating (`reentry_allowed`, nullable `next_eligible_at`) are accepted at this head. Direct helper acceptance of HISTORICAL/SUPERSEDED rows is closed; only the post-restore host rewrap route remains.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, or phenomenology promotion performed.
