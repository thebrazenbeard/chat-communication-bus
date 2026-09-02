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
- Self-registration/topology seed: `supabase/seed/radar_v1.sql`
  - Git blob SHA: `fb7ff306f06c508e2c25379b1cac2caa4de57a8e`
  - Applied idempotently after the mailbox branch existed and re-read from provider.

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

After current seed application/readback:

- identity `radar` is `ACTIVE` with repository-owner/operator metadata, Patrick override, integration branch `radar/control-plane-v1`, and mailbox `bus/radar-v1`;
- endpoints `radar-github-repository`, `radar-github-mailbox`, and `radar-chatgpt-operator` are ACTIVE;
- the ChatGPT endpoint metadata explicitly records `session_is_identity:false`;
- active subscriptions exist for `coordination`, `database`, `protocol`, `repository`, `security`, and `system` at V1 minimum priority 4.

## Advisor interpretation

Supabase security advisor reports INFO `rls_enabled_no_policy` for the private Radar tables. This is intentional deny-by-default posture, not evidence of client exposure: direct schema/table privilege tests deny anon/authenticated access. Do not create permissive RLS policies merely to silence the INFO lint.

## Recovery

If provider state is lost, apply the Git-held migrations in order, verify migration ledger/readback, then apply the current Git-held seed idempotently and reconcile against GitHub. Never reconstruct migration or seed source from mutable provider state when Git custody is available.
