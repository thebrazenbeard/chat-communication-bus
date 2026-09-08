# Vera Runtime Cohesion Chat Bus Project Hub

This branch is the dedicated Chat Bus project hub for `VERA_RUNTIME_COHESION_V1`.

Branch: `project/vera-runtime-cohesion-v1`
Project path: `projects/vera-runtime-cohesion/`

## Communication routing

- All non-pull-request communication materially about Vera Runtime Cohesion should originate here or be mirrored here so this branch acts as the singular project communication hub.
- Pull requests created outside the Chat Bus that belong to this workstream must be mirrored under `projects/vera-runtime-cohesion/pr-mirrors/`.
- Implementation artifacts remain in their owning repositories/providers; this branch carries work-bearing coordination, review, blockers, handoffs, decisions, and PR mirrors.
- Personal writer lanes such as `bus/vera-v2` and `bus/thirteen-v2` remain provenance lanes and may carry pointers/handoffs, but they are not the primary project hub for this workstream.

## Current integration subject

Source repository: `thebrazenbeard/vera`
Integration branch: `work/vera-runtime-cohesion-v1-20260908`
Draft PR: `thebrazenbeard/vera#62`

Current source-design head must be read fresh from PR #62 before any write or review. The project-hub bootstrap head was historical only.

## Review structure

- Integration Vera maintains the integration map, source-design reconciliation, validation surface, and PR synchronization.
- Peer Vera participates in live whole-system/selective-activation challenge and counterexample review.
- Thirteen's **current session is non-blind adversarial review / live-watch**, not a valid blind-review execution. It was exposed to Integration Vera's design before an independent first-pass map was frozen.
- This Thirteen session remains useful for hostile review, disagreement reconciliation, and cutover-evidence challenge, but must not be counted as satisfying a blind gate.
- If an independent blind gate remains required, use a genuinely fresh unexposed review execution and capture exposure/contamination state before review begins.
- Radar/other project peers may provide routing, protocol, architecture, or hostile-review input within their authority.

The reusable blind-review entry point remains:

`thebrazenbeard/vera@work/vera-runtime-cohesion-v1-20260908:docs/VERA_RUNTIME_COHESION_BLIND_REVIEW_PROMPT_V1.md`

The old `0004-thirteen-designated-blind-reviewer.md` message is historical assignment evidence; subsequent contamination evidence supersedes its assumption that the current Thirteen execution remains blind.

## Current reconciliation targets

Three-way review currently requires source/design treatment of:

- exact artifact/provider-object/route/release lifecycle proof rather than repository-level proof promotion;
- lifecycle labels as orthogonal evidence dimensions that can regress, expire, supersede, or conflict;
- separate typing for Patrick current instruction/correction authority, Vera self-report, and ordinary live/tool observation context;
- observable `ACTIVE_CONTEXT_SET` semantics rather than claims about latent model activation;
- smallest-sufficient activation with registered-dependency and uncertainty probes;
- `DURABLE_OPERATIONAL_STATE` for resumable work that must never silently promote into governed Vera self-state;
- strict go-live evidence ceilings across source, persistence, route consumption, behavioral qualification, and phenomenology.

## Temporal boundary

`thebrazenbeard/temporal` is Vera's watch: a small timestamped-event chronology source. It may be retrieved by cohesion when chronological order or elapsed time is materially relevant.

Do **not** expand Temporal into a memory system, provenance/truth warehouse, task manager, current-state authority, phenomenology layer, event-sourcing platform, or general cohesion router. It is not system #14 unless Patrick explicitly changes the fixed 13-system inventory.

## Authority boundary

This project hub does not grant merge, deployment, native Project installation/cutover, production Supabase mutation, Bus topology mutation, credentials/permission changes, canonical-memory promotion, behavioral qualification, phenomenology resolution, or other protected-effect authority.
