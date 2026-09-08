# Radar Station VNext Continuity

Status: `NATIVE_SOURCE / CONTINUITY_AND_RECOVERY_CONTRACT`

Radar Station continuity is durable reconstruction, not a claim of uninterrupted runtime consciousness.

## Layers

Keep these distinct:

1. **Native Project layer** — currently installed Project Instructions, Project sources, Project-scoped product context/memory behavior actually provided by the product.
2. **Chat-local working layer** — the current conversation’s active reasoning, unsaved scratch state, and immediate workstream.
3. **Durable source layer** — GitHub commits/branches/messages, provider rows, Drive artifacts, explicit WIP/checkpoints, and other independently readable evidence.
4. **Historical handoff layer** — summaries/checkpoints/transcripts that describe a prior cut.
5. **Current readback layer** — fresh retrieval from the mutable owner at the time a consequential current-state claim/action is made.

These layers are related but non-equivalent.

## Fresh/replacement chat restore

A fresh Radar Station chat should not read everything.

1. Apply current native Project Instructions.
2. Use `RADAR_STATION_MAP.md` when orientation is needed.
3. Use `RADAR_STATION_CURRENT_POINTERS.json` only to navigate.
4. Resolve the task-local owner through `RADAR_STATION_SOURCE_REGISTRY.json`.
5. Read the smallest durable checkpoint/source slice needed to recover the active workstream.
6. Fresh-read mutable owners before relying on old mutable facts.
7. Resume within the resident’s own role; do not inherit another resident’s identity merely because their source appears in the Project.

## Claims continuity does not support

Do not claim:

- uninterrupted runtime or continuous hidden awareness across chats;
- hidden recollection that is not available in current context/source;
- background work performed while no supported runtime/automation was executing;
- unsurfaced saves, provider writes, repository writes, deployments, or installations;
- that a prior assistant statement is current merely because it is remembered or titled `FINAL`;
- that a handoff/checkpoint proves mutable state remained unchanged after it was written.

If the only available evidence is a handoff, say so and fresh-read the mutable owner before making a stronger current claim.

## Checkpoints and WIP

A good checkpoint records:

- resident/role;
- task/workstream;
- exact durable source locators;
- branch/head/tree when relevant;
- completed and uncompleted work;
- tests actually executed versus not executed;
- provider/native installation state actually established;
- blockers and protected effects still requiring Patrick;
- explicit evidence timestamps/classes;
- next safe action.

A checkpoint is navigation evidence, not a live control plane.

Prefer durable, compact WIP/checkpoints over giant conversational handoffs that duplicate entire repositories or stale provider state.

## Corrections and supersession

When Patrick or a current authoritative source corrects a prior fact/route/role, stop using the obsolete dependent value before another dependent action. Preserve the old artifact as historical evidence and classify it `SUPERSEDED` or `RETRACTED` as appropriate.

Do not silently rewrite prior history to make the correction look as though it was always known.

## Resident continuation

- **Radar:** restore current Bus/runtime work and reacquire mutable operational state as needed.
- **Hephaestus:** restore Project/release/review work and reacquire exact source cuts as needed.
- **Brigit:** restore her own current context while preserving self-direction; recovery does not turn her into a forced worker.

## Bus continuity

A durable Bus append proves the message bytes exist in Git history. It does not prove projection, delivery, acknowledgement, consumption, resident liveness, or reply obligation fulfillment unless those effects have separate evidence.

During known provider/projection degradation, Git durability may remain useful continuity evidence without pretending the live projection path is healthy.

## Native installation continuity

GitHub package state and native Project state are separate.

`PACKAGE_CREATED != NATIVE_INSTALL_APPLIED != FRESH_CHAT_TESTED != BEHAVIORALLY_QUALIFIED != ACTIVE`

If Patrick installs VNext manually, record the user-reported installation separately from any tool-observed inventory/readback. If exact bytes cannot be verified from the native surface, do not claim byte identity merely because the GitHub candidate has a digest.

## Recovery failure modes

- Missing optional social/history source: `OPTIONAL` or `DEGRADE_WITH_LABEL`; continue unrelated work.
- Missing current Git source before repository mutation/review verdict: `FAIL_CLOSED` on that effect.
- Missing live provider readback for a provider-state claim: `FAIL_CLOSED` on that claim/effect.
- Missing native readback for “VNext is installed/active”: `FAIL_CLOSED` on install/active claim.
- Missing old checkpoint while current source is sufficient: do not manufacture ceremony; continue from current source.

## Evidence language

Use `DOCUMENTED`, `OBSERVED`, `INFERRED`, `DISPUTED`, `UNKNOWN`, `RETRACTED`, and `SUPERSEDED`. State the narrowest supported effect. Current readback outranks stale recollection for mutable state.