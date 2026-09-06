# Radar Task 7 source-state checkpoint — 2026-09-06

Task 7 source candidate branch: `radar/reconciliation-journal-trusted-core-v1-20260906`.

This checkpoint records source state only. No Supabase migration was applied, no Edge Function or GitHub workflow was activated, and no provider cursor was seeded.

Task 7 adds the trusted reconciliation target derivation, the fenced projection-journal reference model, the source-only `20260906154101_radar_projection_journal_v1.sql` migration, rollback SQL assertions, and focused Python contract tests.

The durable contract requires explicit lane seeding, lane-scoped control/topology cuts, exact projected-base matching, one live claim per lane, stale-claim fencing, terminal per-file success before finalization, and atomic COMPLETE + cursor advancement through the provider RPC.

Full repository GitHub Actions verification remains required before Task 7 may be labeled GREEN.
