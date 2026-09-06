# Radar Recovery

Radar is designed so loss of a ChatGPT conversation, Realtime connection, or Supabase projection does not erase canonical architecture/source. GitHub is canonical. Provider state is a rebuildable projection and must be read back, never guessed.

## Fresh operator/session recovery

1. Read `RADAR.md`, `architecture/contracts/RADAR_CURRENT.json`, and `architecture/contracts/RADAR_AUTHORITY_V1.md`.
2. Read `architecture/contracts/RADAR_TOPOLOGY_V1.json` for current routing authority.
3. Read `architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json` and the current source migration chain.
4. Treat `architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json` and dated Phase/Cutover documents as historical evidence only. Do not apply historical writer-lane snapshots as current topology.
5. Fresh-read GitHub `main`, current open implementation PRs, ACTIVE writer lanes, and CI.
6. Fresh-read the Supabase migration ledger, Edge configuration, and projection state if provider access is available.
7. Reconcile GitHub canonical/source state against provider readback before any provider-bound action.

A chat transcript can supply useful provenance but is not canonical runtime state.

## GitHub-only degraded mode

If Supabase is unavailable, continue GitHub source/protocol/issue/PR/lane work. Treat provider liveness, queues, subscriptions, projection cursors, telemetry, and DLQ state as unavailable/stale. Do not reconstruct provider currentness from old screenshots, chats, or historical receipts. Record provider-bound work as pending reconciliation.

## Rebuilding the Supabase projection

This procedure describes recovery order; it is not authorization to perform provider effects.

1. Confirm project/schema from `architecture/contracts/RADAR_SUPABASE_V1.md` and currentness from `RADAR_CURRENT.json`.
2. Verify `architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json`; run `python scripts/radar_source_hashes.py` successfully.
3. Fresh-read the provider migration ledger. Compare it with every Git-held `supabase/migrations/*_radar_*.sql` in lexical/version order.
4. Apply only missing Git-held migrations, in exact source order, using the normal migration mechanism. Never reconstruct SQL from mutable provider definitions when Git source exists.
5. Rebuild a clean local database with `supabase db reset`, then run every `supabase/tests/radar_*.sql` with `ON_ERROR_STOP` before provider cutover.
6. Confirm function ACLs, RLS, Realtime publication membership, node lease semantics, replay guard, and projection-journal RPCs after migration.
7. Apply the current `supabase/seed/radar_v1.sql` idempotently only after the full current chain exists. The seed registers `bus/radar-v2` and an OFFLINE node; it must not be treated as heartbeat/lease evidence.
8. Read back Radar identity, node, endpoints, node-bound subscriptions, tables, privileges, and publication membership.
9. Reconcile the current `RADAR_TOPOLOGY_V1.json`; historical cutover lane maps are evidence only.
10. Projection cursor bootstrap is a protected cutover effect. Seed each ACTIVE lane cursor only from reviewed activation/cutover evidence; never infer a cursor from branch naming or replay the entire inherited branch tree.
11. Before enabling central projection, verify the Edge function has the intended custom-auth gateway setting (`verify_jwt` must not preempt the function's GitHub OIDC verifier), and verify provider `RADAR_TRUSTED_PROJECTOR_SHA` equals the reviewed immutable projection anchor B.
12. Deploy/reconfigure Edge and activate the default-branch dispatcher only under separate authorization, then canary one lane and read back cursor/message/journal state before broader use.

## Partial or uncertain write

For a write that returns an error or times out, do not blindly retry. Inspect durable state first. Projection retries use a fresh OIDC token/JTI; business idempotency remains message/content based. A lost/expired journal claim must never advance the projection cursor.

## DLQ recovery

A dead-letter message is not automatically replayable. Refresh the target/current task and applicability first. Preserve the original failure and any replay receipt.

## Diverged writer history

If the durable projection cursor and current writer head are not ancestor-related, fail closed as `DIVERGED_HISTORY`. Do not force-push, synthesize ancestry, or advance the cursor. Preserve the branch and investigate/reconcile explicitly.

## Historical cutover failure

Never repair a historical cutover by rewriting preserved history. Use a successor source repair/PR, verify it independently, and reconcile provider projection to the corrected current source.
