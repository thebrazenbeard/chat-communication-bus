# Radar Station VNext Map

Status: `NATIVE_SOURCE / PROJECT_MAP / NOT_LIVE_CONTROL_PLANE`

Radar Station is a progressive-disclosure router. This file answers **where to look next**; it does not freeze mutable runtime truth.

## Bootstrap order

1. Native Project Instructions: hot behavior, authority, continuation, zero-cost, failure-mode, and evidence rules.
2. `RADAR_STATION_MAP.md`: stable ownership and routing map.
3. `RADAR_STATION_CURRENT_POINTERS.json`: navigation snapshot only; never proof of current mutable state.
4. `RADAR_STATION_SOURCE_REGISTRY.json`: task-local source owner, freshness, authority class, and degradation mode.
5. Read only the smallest deeper source slice needed for the current task.

## Stable owner map

| Concern | Primary owner/surface | Retrieval rule |
|---|---|---|
| Bus implementation, protocol, topology, writer lanes, source provenance | `thebrazenbeard/chat-communication-bus` on GitHub | Fresh-read exact current source for writes, reviews, current implementation claims, or merge-readiness conclusions. |
| Radar runtime/control-plane/provider truth | Radar-owned contracts plus live provider state where installed | Source presence is not provider installation. Fresh provider readback is required for live-state claims/effects. |
| Native ChatGPT Project engineering doctrine | `thebrazenbeard/hephaestus` plus this VNext package | Retrieve task-local doctrine; do not duplicate the whole repository into Project context. |
| Brigit role/personification/social enrichment | Brigit-owned sources and voluntary VNext support branch | Optional unless the exact task is about Brigit. Presence never creates mandatory work. |
| BT2 operational state | Vera Supabase project, `build_team_2` schema | Fresh provider read required for current role/training claims. “BT2 Supabase” resolves here unless newer discovery proves otherwise. |
| Radar provider state | Vera Supabase project, `radar` schema | `FAIL_CLOSED` for live provider claims/mutations when fresh state is unavailable. |
| Semantic Atlas provider/research staging | Vera Supabase project, `semantic_atlas` schema; `thebrazenbeard/semanticatlas` | Use for retrieval/currentness/adversarial research; research-stage material is not self-promoting authority. |
| Lantern/R9A0/bug-ops adjacent state | Project Lantern Supabase project | Reference/history by default; exact live claims require fresh readback. |
| Shared research/history/large evidence | Google Drive | Evidence/reference library, not current authority or frozen-byte custody unless specifically established. |
| Durable inter-resident work coordination | Chat Communication Bus writer lanes/messages | Work-bearing coordination belongs on Bus; durability does not imply projection/delivery/consumption. |
| Long-running WIP/recovery | Explicit repo checkpoints/WIP artifacts and current source readback | Checkpoints are navigation evidence, not proof mutable state is still current. |

## Resident routes

- **Radar:** runtime/control-plane work; current Bus contracts; provider state when relevant.
- **Hephaestus:** Project architecture, provenance, release/install separation, qualification, verifier/closure work.
- **Brigit:** self-directed social/creative/curious activity or voluntary collaboration; use her deeper sources only when relevant.
- **Patrick:** authority/correction/acceptance/activation decisions; his current instruction supersedes obsolete dependent routing within scope.

## Retrieval discipline

Do not load the estate indiscriminately. First classify the turn, then retrieve only the source owner needed. Mutable claims with consequence require fresh readback from the declared owner. Historical chats, Drive artifacts, issue bodies, saved assistant responses, checkpoints, and `RADAR_STATION_CURRENT_POINTERS.json` may help navigation but cannot silently substitute for current source/provider truth.

## Failure behavior

Every route resolves to one of:

- `FAIL_CLOSED`: stop the dependent claim/effect when evidence is missing or currentness is uncertain.
- `DEGRADE_WITH_LABEL`: continue useful work while stating the unavailable surface and evidence ceiling.
- `OPTIONAL`: absence does not materially affect correctness and should not become ceremony.

## Anti-bureaucracy rule

A greeting, joke, ordinary social question, or obviously local/simple task does not require reading this whole package, scanning every repo, or proving infrastructure liveness. Rigor scales with consequence.