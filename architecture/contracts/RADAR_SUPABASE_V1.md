# RADAR_SUPABASE_V1

Provider target: existing healthy Vera Supabase project `klmbpaigzeguvnpccqzz`, isolated schema `radar`.

GitHub remains canonical source. Provider state is a rebuildable projection/runtime and does not become canonical merely because it exists.

## Source custody

Base migration: `supabase/migrations/20260902_radar_control_plane_v1.sql`

- Git blob SHA: `aa383ca0aa80dc10a0ef924a0e80369da4b8b623`
- Git object/file byte length observed: `13799`
- Provider migration name/version: `radar_control_plane_v1` / `20260902120716`
- Provider ledger statement count: `1`
- Provider ledger stored bytes: `13799`
- Provider ledger stored-statement SHA-256: `7e644e63f6fbe6ae9747043aa502f9c9c1bda42e8ec6fd99da6bbfaf0436b607`

Realtime migration: `supabase/migrations/20260902_radar_realtime_v1.sql`

- Git blob SHA: `ee3a8a4a6d4161e348d009e27ca71d0048ac6f31`
- Git object/file byte length observed: `721`
- Provider migration name/version: `radar_realtime_v1` / `20260902120826`
- Provider ledger statement count: `1`
- Provider ledger stored bytes: `721`
- Provider ledger stored-statement SHA-256: `0ef94f8a25ad0b68c354784ee460739a7ac4966496311d828ce9427a2c227be1`

Self-registration/topology seed: `supabase/seed/radar_v1.sql`

- Current Git blob SHA: `fb7ff306f06c508e2c25379b1cac2caa4de57a8e`
- Applied idempotently after `bus/radar-v1` existed and fresh-read from provider.

Git SHA-256 receipts are emitted by `scripts/radar_source_hashes.py` in CI. Provider migration SHA-256 values above are computed independently from the provider migration ledger. Exact equality between the Git and provider SHA-256 receipts must be established before Phase 19 cutover; matching byte counts alone are not treated as sufficient proof.

## Provider readback

Fresh read-only inspection established:

- `radar` schema exists.
- 14 expected control tables exist and all have RLS enabled.
- `anon` and `authenticated` have no `radar` schema USAGE and zero Radar table grants.
- functions `assignment_ready`, `mark_stale_nodes_offline`, `prevent_dependency_cycle`, `prevent_event_mutation`, and `touch_node` exist in the `radar` schema.
- the provider migration ledger contains both migrations above.

The repository contains transactional verification source at `supabase/tests/radar_control_plane_v1.sql` and `supabase/tests/radar_realtime_v1.sql`. This contract does **not** claim those transactional scripts were executed in the current operator pass; source existence is not a provider test receipt.

## Realtime readback

`supabase_realtime` currently publishes exactly these Radar low-volume control projections:

- `acknowledgements`
- `assignments`
- `dependencies`
- `nodes`
- `reconciliation_events`

High-volume `messages`, `delivery_events`, and `telemetry` are deliberately excluded from Postgres Changes.

## Self-registration readback

Fresh provider inspection established:

- identity `radar` is `ACTIVE` with repository-owner/operator metadata, Patrick override, integration branch `radar/control-plane-v1`, and mailbox `bus/radar-v1`;
- endpoints `radar-github-repository`, `radar-github-mailbox`, and `radar-chatgpt-operator` are `ACTIVE`;
- the ChatGPT endpoint metadata explicitly records `session_is_identity:false`;
- active subscriptions exist for `coordination`, `database`, `protocol`, `repository`, `security`, and `system`, each at V1 minimum priority 4.

## Security interpretation

Radar intentionally has no anon/authenticated schema/table access at V1. Do not add permissive RLS policies merely to make a generic lint quiet; evaluate actual grants, schema exposure, and intended client model first.

## Recovery

If provider state is lost, apply the Git-held migrations in order, verify migration-ledger/readback, then apply the current Git-held seed idempotently and reconcile against GitHub. Never reconstruct migration or seed source from mutable provider state when Git custody is available.
