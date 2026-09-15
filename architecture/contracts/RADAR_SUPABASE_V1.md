# RADAR_SUPABASE_V1

Provider target: Supabase project `klmbpaigzeguvnpccqzz`, isolated schema `radar`.

GitHub remains canonical source. Supabase is a rebuildable projection/runtime and never becomes canonical merely because state exists there. Provider effects require separate authorization.

## Current source custody

Current source/recovery authority is `architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json` plus the ordered `supabase/migrations/*_radar_*.sql` chain. Historical short migration filenames in older receipts are not current recovery paths.

The current Radar source chain, through 2026-09-08, is:

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
14. `20260908010500_radar_projection_atomic_file_v1.sql`

## Provider readback boundary

The last recorded provider readback is dated 2026-09-06. At that readback, the provider migration ledger contained Radar migrations only through `20260903113314_radar_operator_views_v1`. Six later source migrations in the current Git chain are therefore unapplied relative to that recorded provider state:

- thread-closure semantics;
- durable GitHub OIDC JTI replay guard;
- node-bound routing/lease hardening;
- projection lane/batch/file journal;
- journal PostgREST API;
- atomic claim-bound file projection.

The recorded provider therefore remains `PARTIAL_NOT_CURRENT` relative to current Git source. This section is historical readback status, not a claim that the provider was freshly queried after 2026-09-06.

The recorded live Edge function `github-bus-ingest` is ACTIVE version 3 with `verify_jwt=true`. That gateway setting preempts the intended custom GitHub OIDC admission path before the function's verifier can admit a GitHub Actions OIDC bearer. The current body-bound Edge source, replay guard, projection journal/API, atomic claim-bound file projection, and projection cursors are not established as live provider state by the recorded readback.

These facts are status evidence only. They do not authorize migration application, Edge deployment, changing `verify_jwt`, setting `RADAR_TRUSTED_PROJECTOR_SHA`, seeding projection cursors, or activating the dispatcher.

## Current self-registration model

Current mailbox: `bus/radar-v2`.

`supabase/seed/radar_v1.sql` is the current idempotent projection seed despite its historical filename. It must be run only after the full current migration chain. It creates/updates:

- Radar identity metadata pointing at `bus/radar-v2`;
- one stable recovery/operator node in `OFFLINE` state with no heartbeat or lease;
- repository, mailbox, and operator endpoints;
- node-bound active subscriptions for the configured Radar domains.

The seed deliberately does not call `touch_node()` and therefore cannot establish runtime liveness or routing authority by itself.

Historical references to predecessor mailbox/control branches remain provenance only.

## Node-level routing security

Once `20260906133630_radar_node_routing_hardening_v1.sql` is applied, active subscriptions must be node-bound, node ownership is immutable, routable nodes require current leases, NULL/expired leases fail closed, and successful heartbeats renew a bounded lease. The same migration closes the historical default-PUBLIC EXECUTE gap for `assignment_ready`, `mark_stale_nodes_offline`, and `touch_node`.

## Realtime currentness

Historical September-2 documentation that described exactly five low-volume Radar publication tables is superseded. Later source migrations add additional publication members where appropriate. Recovery verification must inspect actual publication membership after rebuilding the full current chain and run the current SQL assertions; do not use the old five-table list as a present-tense invariant.

## Projection trust and atomic journal boundary

Current source design uses:

- a default-branch central dispatcher with `workflow_run` wakeup plus five-minute scheduled backstop;
- immutable reusable trusted-projector source selected by exact commit SHA;
- writer branches as inert Git objects, never executable trusted source;
- remote-tracking writer-ref reads without materializing local writer branches;
- durable per-lane projection cursors plus fenced batch/file journal state;
- exact-body SHA-256-bound GitHub OIDC audience/header;
- fresh JTI per request, consumed after cryptographic body binding and before semantic JSON parsing;
- atomic claim-bound file projection through `radar_projection_project_file_v1`;
- one SQL transaction that validates the claim token/lease, lane cursor, control/topology cut, exact claimed path, sender/source binding, message projection result, and terminal journal state;
- normalized claim-sensitive lock order `lane -> batch -> file`;
- service-role revocation of the legacy standalone message-projection and standalone file-result mutation paths after the atomic-file migration.

Provider `RADAR_TRUSTED_PROJECTOR_SHA` may be set only to the exact immutable successor projector source cut bound by an authoritative local PASS receipt and the current reviewed contracts. Historical frozen projector references are evidence only and are not valid deployment targets merely because they were previously current.

None of these source properties should be interpreted as a live-provider claim until migration/deployment/configuration/cursor readback proves the effect.

## Provider access planes

Radar keeps provider write ingress, provider management, and provider qualification/readback as separate trust planes. The official `supabase-py` client is the preferred optional client for independent read-only data-plane readback. Its results remain non-canonical evidence and do not supersede Git custody or exact source qualification.

`supabase-py` does not replace provider management: migration-ledger inspection, migration application, Edge deployment/configuration, secrets, and gateway metadata still require the reviewed provider-management/CLI path. It also does not replace GitHub OIDC ingress: the trusted projector still obtains a GitHub Actions OIDC token and sends it to `github-bus-ingest`, whose reviewed configuration remains `verify_jwt = false` so the function's custom GitHub OIDC verifier can authenticate that non-Supabase token.

The guaranteed SDK readback surface in the current source design is the read-only public RPC `public.radar_projection_get_lane_v1`. Reads of `radar.identity_message_status_v2` and `radar.open_assignments_v1` are useful capability probes only when the `radar` schema is exposed through PostgREST; source grants alone do not prove that exposure. No generic table or RPC mutation escape hatch belongs in the readback adapter.

External gateways such as Cloudflare Workers, Envoy, Kong, or APISIX may be evaluated later as defense-in-depth or self-hosting components, but none is a required dependency for the hosted recovery path. PostgreSQL-wire gatekeepers such as `jit-db-gatekeeper` or `pg-gateway` are self-hosting/future architecture references, not current hosted-provider controls.

## Qualification boundary

Private hosted GitHub Actions are non-authoritative for Radar. The authoritative qualification route is `LOCAL_NO_PAID_SERVICES` through `scripts/radar_local_qualify.ps1` under `architecture/contracts/RADAR_QUALIFICATION_V1.json`.

An authoritative local PASS receipt must bind the exact successor source commit, source tree, and clean working tree before that source cut can be treated as deployment-eligible. Static review, historical action receipts, or a previously frozen projector reference are not substitutes.

## Historical provider receipts

September-2 receipts showing exact custody and successful tests for the base control/realtime migrations remain valid historical evidence at the scope they actually tested. Later historical projector/action receipts likewise remain evidence only at their original scope. Those receipts do not establish currentness for later migrations, current writer lanes, current Realtime publication membership, atomic projection, or the current projection trust chain.

## Recovery rule

Follow `docs/operator/RECOVERY.md`: verify source custody and the authoritative local PASS receipt, rebuild/test the full Git-held chain locally, compare provider ledger to source, apply only missing migrations under separate authorization, seed current registration only after the chain exists, deliberately bootstrap projection cursors from reviewed activation evidence, configure only the exact qualified immutable successor projector SHA, and canary the complete Git -> OIDC -> Edge -> atomic projection -> journal finalize -> provider readback path before broader activation. Never recover current topology from dated cutover snapshots or mutable provider definitions when canonical Git source exists.
