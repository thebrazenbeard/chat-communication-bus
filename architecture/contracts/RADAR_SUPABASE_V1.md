# RADAR_SUPABASE_V1

Provider target: existing healthy Vera Supabase project `klmbpaigzeguvnpccqzz`, isolated schema `radar`.

GitHub remains canonical source. Provider state is a rebuildable projection/runtime and does not become canonical merely because it exists.

## Source custody

- Base migration: `supabase/migrations/20260902_radar_control_plane_v1.sql`
  - Git blob SHA: `aa383ca0aa80dc10a0ef924a0e80369da4b8b623`
  - Provider migration name: `radar_control_plane_v1`
  - Provider migration version observed after application: `20260902120716`
- Realtime migration: `supabase/migrations/20260902_radar_realtime_v1.sql`
  - Git blob SHA: `ee3a8a4a6d4161e348d009e27ca71d0048ac6f31`
  - Provider migration name: `radar_realtime_v1`
  - Provider migration version observed after application: `20260902120826`

## Provider readback

After base migration application:

- `radar` schema exists.
- 14 expected control tables exist with RLS enabled.
- `anon` and `authenticated` have neither schema USAGE nor tested SELECT/INSERT table privileges.
- Transactional provider contract `supabase/tests/radar_control_plane_v1.sql` passed, including stale-node liveness, identity preservation, dependency readiness, and durable DLQ assertions.

After Realtime migration application, `supabase_realtime` contains exactly these Radar control projections at V1 bootstrap:

- `acknowledgements`
- `assignments`
- `dependencies`
- `nodes`
- `reconciliation_events`

High-volume `messages`, `delivery_events`, and `telemetry` are deliberately excluded from Postgres Changes.

## Advisor interpretation

Supabase security advisor reports INFO `rls_enabled_no_policy` for the private Radar tables. This is intentional deny-by-default posture, not evidence of client exposure: direct schema/table privilege tests deny anon/authenticated access. Do not create permissive RLS policies merely to silence the INFO lint.

## Recovery

If provider state is lost, apply the Git-held migrations in order, verify migration ledger/readback, then reseed Radar identity/topology and reconcile against GitHub. Never reconstruct migration source from mutable provider state when Git custody is available.
