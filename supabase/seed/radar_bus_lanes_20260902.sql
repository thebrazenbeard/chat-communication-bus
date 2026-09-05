-- Radar GitHub writer-lane projection snapshot, observed 2026-09-02.
-- Consolidated & parameterized version:
--  - single lane CTE reused for both identity and endpoint inserts
--  - observed_date is parameterized via the params CTE
--  - transaction wrapper for atomicity
-- Change the observed_date in params if you need a different snapshot date.

BEGIN;

WITH
params AS (
  -- Change here if you want to set a different observed_date for the whole file
  SELECT '2026-09-02'::date AS observed_date
),
lane(identity_id, display_name, branch_name, aliases) AS (
  VALUES
    ('brigit', 'Brigit', 'bus/bridget-v1', ARRAY['bridget']::text[]),
    ('eight', 'Eight', 'bus/eight-v1', '{}'::text[]),
    ('five-five', 'Five-Five', 'bus/five-five-v1', '{}'::text[]),
    ('five', 'Five', 'bus/five-v1', '{}'::text[]),
    ('fng', 'FNG', 'bus/fng-v1', '{}'::text[]),
    ('four', 'Four', 'bus/four-v1', '{}'::text[]),
    ('hephaestus', 'Hephaestus', 'bus/hephaestus-v2', '{}'::text[]),
    ('masa', 'Masa', 'bus/masa-v1', '{}'::text[]),
    ('mune', 'Mune', 'bus/mune-v1', '{}'::text[]),
    ('nine', 'Nine', 'bus/nine-v1', '{}'::text[]),
    ('one', 'One', 'bus/one-v1', '{}'::text[]),
    ('seven', 'Seven', 'bus/seven-v1', '{}'::text[]),
    ('six', 'Six', 'bus/six-v1', '{}'::text[]),
    ('thirteen', 'Thirteen', 'bus/thirteen-v1', '{}'::text[]),
    ('three', 'Three', 'bus/three-v1', '{}'::text[]),
    ('two', 'Two', 'bus/two-v1', '{}'::text[]),
    ('vera', 'Vera', 'bus/vera-sol-v1', ARRAY['vera-sol']::text[]),
    ('yang', 'Yang', 'bus/yang-v1', '{}'::text[]),
    ('yin', 'Yin', 'bus/yin-v1', '{}'::text[])
)

-- Insert / upsert identities
INSERT INTO radar.identities (identity_id, display_name, aliases, lifecycle_status, metadata)
SELECT
  l.identity_id,
  l.display_name,
  l.aliases,
  'ACTIVE',
  jsonb_build_object(
    'projection_basis', 'github_writer_lane_observed',
    'observed_branch', l.branch_name,
    'observed_date', p.observed_date,
    'liveness_claimed', false
  )
FROM lane l
CROSS JOIN params p
ON CONFLICT (identity_id) DO UPDATE
SET
  display_name = EXCLUDED.display_name,
  aliases = EXCLUDED.aliases,
  metadata = EXCLUDED.metadata,
  updated_at = now();

-- Insert / upsert endpoints
INSERT INTO radar.endpoints (endpoint_id, identity_id, transport, address, status, metadata)
SELECT
  'lane-' || l.identity_id,
  l.identity_id,
  'github_branch',
  l.branch_name,
  'ACTIVE',
  jsonb_build_object(
    'role', 'sole_writer_mailbox_projection',
    'projection_basis', 'github_writer_lane_observed',
    'liveness_claimed', false,
    'observed_date', p.observed_date
  )
FROM lane l
CROSS JOIN params p
ON CONFLICT (endpoint_id) DO UPDATE
SET
  identity_id = EXCLUDED.identity_id,
  transport = EXCLUDED.transport,
  address = EXCLUDED.address,
  status = EXCLUDED.status,
  metadata = EXCLUDED.metadata,
  updated_at = now();

COMMIT;
