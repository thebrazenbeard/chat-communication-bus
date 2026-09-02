# Radar Recovery

Radar is designed so loss of a ChatGPT conversation, live Realtime connection, or Supabase projection does not erase canonical architecture/source.

## Fresh ChatGPT session

1. Read `RADAR.md`.
2. Read `architecture/contracts/RADAR_AUTHORITY_V1.md` and `docs/protocol/PROTOCOL_V2.md`.
3. Read the current design/operator contract and Phase 19 checklist.
4. Fresh-read GitHub `main`, `radar/control-plane-v1`/successor, PR status, writer lanes, and CI.
5. Fresh-read Supabase migration ledger and `radar` projection if provider is available.
6. Reconcile GitHub canonical/source state against provider projection.
7. Surface material exceptions only, then continue the current task.

A chat transcript can supply useful provenance but is not required canonical runtime state.

## GitHub-only degraded mode

If Supabase is unavailable:

- Keep GitHub source/protocol/issue/PR/lane work operating normally.
- Treat liveness, provider queues, dependency projection, telemetry, and DLQ provider state as unavailable/stale rather than guessing.
- Do not reconstruct provider currentness from old screenshots/chat claims.
- Record any provider-bound actions as pending reconciliation.
- When Supabase returns, read migration ledger first, then projection state, then reconcile before replaying queued effects.

## Rebuilding Supabase projection

1. Confirm provider/project target from `architecture/contracts/RADAR_SUPABASE_V1.md`.
2. Fresh-read Git migration files; do not copy SQL out of mutable provider state when Git source exists.
3. Check migration ledger before applying each migration.
4. Apply missing Git-held migrations in order.
5. Run `supabase/tests/radar_control_plane_v1.sql` and `supabase/tests/radar_realtime_v1.sql` against the target.
6. Apply `supabase/seed/radar_v1.sql` idempotently.
7. Read back Radar identity, endpoints, subscriptions, tables, privileges, and publication membership.
8. Reconcile current GitHub branch/lane/protocol state into the rebuilt provider projection.

## Partial / uncertain write

For a non-idempotent write that returns an error or times out, do not blindly retry. Inspect whether the intended effect committed. If exact effect state cannot be established, preserve ambiguity and use a successor/recovery operation rather than double-applying it.

## DLQ recovery

A dead-letter message is not automatically eligible for replay. Refresh the target/current task and set applicability first. Replay only if still applicable. Preserve the original failure and replay receipt.

## Cutover failure

Never repair a bad Phase 19 cutover by force-pushing historical `main`. Preserve the failed state, revert or create a successor repair branch/PR, verify it independently, and reconcile provider projections to the corrected canonical head.
