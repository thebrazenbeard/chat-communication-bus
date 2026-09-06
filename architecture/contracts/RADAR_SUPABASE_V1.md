# RADAR_SUPABASE_V1

Provider target: Supabase project `klmbpaigzeguvnpccqzz`, isolated schema `radar`.

GitHub remains canonical source. Supabase is a rebuildable projection/runtime and never becomes canonical merely because state exists there. Provider effects require separate authorization.

## Current source custody

Current source/recovery authority is `architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json` plus the ordered `supabase/migrations/*_radar_*.sql` chain. Historical short migration filenames in older receipts are not current recovery paths.

The current Radar source chain, through 2026-09-06, is:

1. `20260902120716_radar_control_plane_v1.sql`
2. `20260902120826_radar_realtime_v1.sql`
3. `20260902203610_radar_visual_identity_v1.sql`
4. `20260902204759_radar_live_message_projection_v1.sql`
5. `20260902231445_radar_live_message_collision_v1.sql`
6. `20260903000603_radar_receipt_plane_v1.sql`
7. `20260903001906_radar_assignment_plane_v1.sql`
8. `20260903113314_radar_operator_views_v1.sql`
9. `20260903214334_radar_thread_closure_v1.sql`
10. `20260905230823_radar_oidc_replay_guard_v1.sql`
11. `20260906133630_radar_node_routing_hardening_v1.sql`
12. `20260906154101_radar_projection_journal_v1.sql`
13. `20260906165117_radar_projection_journal_api_v1.sql`

## Fresh provider readback — 2026-09-06

The provider migration ledger currently contains Radar migrations only through `20260903113314_radar_operator_views_v1`. The five later source migrations above are not applied.

Readback also confirms the provider does not currently have the GitHub OIDC replay-guard table, projection-journal lane/batch tables, or the projection-journal public RPC bridge. Therefore provider state is `PARTIAL_NOT_CURRENT` relative to Git source.

The live Edge function `github-bus-ingest` is ACTIVE version 3 with `verify_jwt=true`. That gateway setting currently preempts the intended custom GitHub OIDC admission path. Immutable projection anchor B (`7076c73595d5a572e0f374c3a495b29982d92bed`) and its body-bound Edge source are source-only and are not deployed/configured in the provider.

These facts are status evidence only. They do not authorize migration application, Edge deployment, changing `verify_jwt`, setting `RADAR_TRUSTED_PROJECTOR_SHA`, or seeding projection cursors.

## Current self-registration model

Current mailbox: `bus/radar-v2`.

`supabase/seed/radar_v1.sql` is the current idempotent projection seed despite its historical filename. It must be run only after the full current migration chain. It creates/updates:

- Radar identity metadata pointing at `bus/radar-v2`;
- one stable recovery/operator node in `OFFLINE` state with no heartbeat or lease;
- repository, mailbox, and operator endpoints;
- node-bound active subscriptions for the configured Radar domains.

The seed deliberately does not call `touch_node()` and therefore cannot establish runtime liveness or routing authority by itself.

Historical references to `bus/radar-v1` or `radar/control-plane-v1` remain provenance only.

## Node-level routing security

Once `20260906133630_radar_node_routing_hardening_v1.sql` is applied, active subscriptions must be node-bound, node ownership is immutable, routable nodes require current leases, NULL/expired leases fail closed, and successful heartbeats renew a bounded lease. The same migration closes the historical default-PUBLIC EXECUTE gap for `assignment_ready`, `mark_stale_nodes_offline`, and `touch_node`.

## Realtime currentness

Historical September-2 documentation that described exactly five low-volume Radar publication tables is superseded. Later source migrations add additional publication members where appropriate. Recovery verification must inspect actual publication membership after rebuilding the full current chain and run the current SQL assertions; do not use the old five-table list as a present-tense invariant.

## Projection trust chain

Current source design uses:

- default-branch central dispatcher with `workflow_run` wakeup plus five-minute scheduled backstop;
- immutable reusable trusted projector anchored by exact commit SHA;
- writer branches as inert Git objects, never executable trusted source;
- durable per-lane projection cursors and fenced batch/file journal state;
- exact-body SHA-256-bound GitHub OIDC audience/header;
- fresh JTI per request, consumed after cryptographic body binding and before semantic JSON parsing;
- deploy-time `RADAR_TRUSTED_PROJECTOR_SHA` equal to reviewed immutable projection anchor B.

None of those source properties should be interpreted as a live-provider claim until migration/deployment/configuration/cursor readback proves the effect.

## Historical provider receipts

September-2 receipts showing exact custody and successful tests for the base control/realtime migrations remain valid historical evidence at the scope they actually tested. The Vera logical-identity repair is likewise historical evidence. Those receipts do not establish currentness for later migrations, current writer lanes, current Realtime publication membership, or the current projection trust chain.

## Recovery rule

Follow `docs/operator/RECOVERY.md`: verify source custody, rebuild/test the full Git-held chain locally, compare provider ledger to source, apply only missing migrations under authorization, seed current registration only after the chain exists, then explicitly bootstrap projection cursors from reviewed activation evidence. Never recover current topology from dated cutover snapshots or mutable provider definitions when canonical Git source exists.
