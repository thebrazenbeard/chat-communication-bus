-- Radar GitHub writer-lane projection snapshot, observed 2026-09-02.
-- GitHub branch existence is durable routing/provenance evidence, not node liveness.
-- Radar itself is seeded by radar_v1.sql; this snapshot projects the other observed lanes.

begin;

with lane(identity_id, display_name, branch_name) as (
  values
    ('brigit', 'Brigit', 'bus/bridget-v1'),
    ('eight', 'Eight', 'bus/eight-v1'),
    ('five-five', 'Five-Five', 'bus/five-five-v1'),
    ('five', 'Five', 'bus/five-v1'),
    ('fng', 'FNG', 'bus/fng-v1'),
    ('four', 'Four', 'bus/four-v1'),
    ('hephaestus', 'Hephaestus', 'bus/hephaestus-v2'),
    ('masa', 'Masa', 'bus/masa-v1'),
    ('mune', 'Mune', 'bus/mune-v1'),
    ('nine', 'Nine', 'bus/nine-v1'),
    ('one', 'One', 'bus/one-v1'),
    ('seven', 'Seven', 'bus/seven-v1'),
    ('six', 'Six', 'bus/six-v1'),
    ('thirteen', 'Thirteen', 'bus/thirteen-v1'),
    ('three', 'Three', 'bus/three-v1'),
    ('two', 'Two', 'bus/two-v1'),
    ('vera', 'Vera', 'bus/vera-sol-v1'),
    ('yang', 'Yang', 'bus/yang-v1'),
    ('yin', 'Yin', 'bus/yin-v1')
)
insert into radar.identities(identity_id, display_name, aliases, lifecycle_status, metadata)
select
  identity_id,
  display_name,
  case when identity_id = 'brigit' then array['bridget']::text[]
       else case when identity_id = 'vera' then array['vera-sol']::text[] else '{}'::text[] end
  end,
  'ACTIVE',
  jsonb_build_object(
    'projection_basis', 'github_writer_lane_observed',
    'observed_branch', branch_name,
    'observed_date', '2026-09-02',
    'liveness_claimed', false
  )
from lane
on conflict (identity_id) do update
set display_name = excluded.display_name,
    aliases = excluded.aliases,
    metadata = excluded.metadata,
    updated_at = now();

with lane(identity_id, branch_name) as (
  values
    ('brigit', 'bus/bridget-v1'),
    ('eight', 'bus/eight-v1'),
    ('five-five', 'bus/five-five-v1'),
    ('five', 'bus/five-v1'),
    ('fng', 'bus/fng-v1'),
    ('four', 'bus/four-v1'),
    ('hephaestus', 'bus/hephaestus-v2'),
    ('masa', 'bus/masa-v1'),
    ('mune', 'bus/mune-v1'),
    ('nine', 'bus/nine-v1'),
    ('one', 'bus/one-v1'),
    ('seven', 'bus/seven-v1'),
    ('six', 'bus/six-v1'),
    ('thirteen', 'bus/thirteen-v1'),
    ('three', 'bus/three-v1'),
    ('two', 'bus/two-v1'),
    ('vera', 'bus/vera-sol-v1'),
    ('yang', 'bus/yang-v1'),
    ('yin', 'bus/yin-v1')
)
insert into radar.endpoints(endpoint_id, identity_id, transport, address, status, metadata)
select
  'lane-' || identity_id,
  identity_id,
  'github_branch',
  branch_name,
  'ACTIVE',
  jsonb_build_object(
    'role', 'sole_writer_mailbox_projection',
    'projection_basis', 'github_writer_lane_observed',
    'liveness_claimed', false,
    'observed_date', '2026-09-02'
  )
from lane
on conflict (endpoint_id) do update
set identity_id = excluded.identity_id,
    transport = excluded.transport,
    address = excluded.address,
    status = excluded.status,
    metadata = excluded.metadata,
    updated_at = now();

commit;
