# RADAR_SUPABASE_V1

Provider target: existing healthy Vera Supabase project `klmbpaigzeguvnpccqzz`, isolated schema `radar`.

GitHub remains canonical source. Provider state is a rebuildable projection/runtime and does not become canonical merely because it exists.

## Source custody

Base migration: `supabase/migrations/20260902_radar_control_plane_v1.sql`

- Git blob SHA: `aa383ca0aa80dc10a0ef924a0e80369da4b8b623`
- Git byte length: `13799`
- Git SHA-256 from CI run 101: `7e644e63f6fbe6ae9747043aa502f9c9c1bda42e8ec6fd99da6bbfaf0436b607`
- Provider migration name/version: `radar_control_plane_v1` / `20260902120716`
- Provider ledger statement count: `1`
- Provider ledger stored bytes: `13799`
- Provider ledger stored-statement SHA-256: `7e644e63f6fbe6ae9747043aa502f9c9c1bda42e8ec6fd99da6bbfaf0436b607`
- Custody result: **EXACT_SHA256_MATCH**.

Realtime migration: `supabase/migrations/20260902_radar_realtime_v1.sql`

- Git blob SHA: `ee3a8a4a6d4161e348d009e27ca71d0048ac6f31`
- Git byte length: `721`
- Git SHA-256 from CI run 101: `0ef94f8a25ad0b68c354784ee460739a7ac4966496311d828ce9427a2c227be1`
- Provider migration name/version: `radar_realtime_v1` / `20260902120826`
- Provider ledger statement count: `1`
- Provider ledger stored bytes: `721`
- Provider ledger stored-statement SHA-256: `0ef94f8a25ad0b68c354784ee460739a7ac4966496311d828ce9427a2c227be1`
- Custody result: **EXACT_SHA256_MATCH**.

Self-registration/topology seed: `supabase/seed/radar_v1.sql`

- Current Git blob SHA: `fb7ff306f06c508e2c25379b1cac2caa4de57a8e`
- Git byte length from CI run 101: `2728`
- Git SHA-256 from CI run 101: `0f6b69c1bdef95dccf1eb353a98e8d80a327f7067fe94b70c85816c2dd8ea026`
- Applied idempotently after `bus/radar-v1` existed and fresh-read from provider.

## Provider readback

Fresh inspection established:

- `radar` schema exists.
- 14 expected control tables exist and all have RLS enabled.
- `anon` and `authenticated` have no `radar` schema USAGE and zero Radar table grants.
- functions `assignment_ready`, `mark_stale_nodes_offline`, `prevent_dependency_cycle`, `prevent_event_mutation`, and `touch_node` exist in the `radar` schema.
- the provider migration ledger contains both migrations above.

Provider verification receipts on 2026-09-02:

- exact Git-held `supabase/tests/radar_realtime_v1.sql` executed as a read-only assertion block and completed without exception: **PASS**.
- exact Git-held `supabase/tests/radar_control_plane_v1.sql` executed under Patrick's authorization. Its temporary fixtures exercised stale-node handling, identity preservation, dependency readiness, privilege assertions, and DLQ state; the transaction completed and rolled back: **PASS**.
- post-test readback found zero `radar-test-a`/`radar-test-b` identities, zero `radar-pred`/`radar-succ` assignments, and zero `radar-test-message` dead letters, confirming fixture rollback.

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

## Vera logical-identity reconciliation

A GitHub/provider reconciliation found provider projection drift where historical route name `vera-sol` had been modeled as a separate active logical identity instead of logical `vera`.

Source correction and provider repair:

- `src/radar/github_projection.py`, `architecture/contracts/RADAR_TOPOLOGY_V1.json`, and `supabase/seed/radar_bus_lanes_20260902.sql` normalize historical branch `bus/vera-sol-v1` to logical identity `vera` while preserving `vera-sol` as an alias/route name.
- exact Git-held repair `supabase/repairs/20260902_normalize_vera_identity.sql` was applied under Patrick's authorization. It performs no DELETE.
- fresh readback: `vera` is `ACTIVE`, aliases include `vera-sol`, and `lane-vera` is `ACTIVE` at `bus/vera-sol-v1`.
- fresh readback: historical `vera-sol` identity is `ARCHIVED` with `superseded_by: vera`; historical `lane-vera-sol` endpoint is `ARCHIVED`, preserves its original branch address in metadata, and points to `lane-vera` as successor.
- no nodes, subscriptions, acknowledgements, delivery-event identity references, health-event references, or delivery-event endpoint references depended on the legacy identity/endpoint at repair time.
- reconciliation result: **RESOLVED_WITH_PROVENANCE_PRESERVED**.

## Security interpretation

Radar intentionally has no anon/authenticated schema/table access at V1. Do not add permissive RLS policies merely to make a generic lint quiet; evaluate actual grants, schema exposure, and intended client model first.

## Recovery

If provider state is lost, apply the Git-held migrations in order, verify migration-ledger/readback, then apply the current Git-held seed idempotently and reconcile against GitHub. Never reconstruct migration or seed source from mutable provider state when Git custody is available.
