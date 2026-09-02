-- Radar provider projection repair: normalize historical `vera-sol` route identity
-- to logical identity `vera` while preserving the legacy provider row as archived
-- provenance. GitHub branch `bus/vera-sol-v1` is not renamed or rewritten.
--
-- This repair is idempotent and intentionally performs no DELETE.

begin;

insert into radar.identities(identity_id, display_name, aliases, lifecycle_status, metadata)
values (
  'vera',
  'Vera',
  array['vera-sol']::text[],
  'ACTIVE',
  jsonb_build_object(
    'projection_basis', 'github_writer_lane_observed',
    'observed_branch', 'bus/vera-sol-v1',
    'logical_identity_normalized', true,
    'legacy_route_identity', 'vera-sol',
    'liveness_claimed', false
  )
)
on conflict (identity_id) do update
set display_name = excluded.display_name,
    aliases = excluded.aliases,
    lifecycle_status = 'ACTIVE',
    metadata = radar.identities.metadata || excluded.metadata,
    updated_at = now();

-- Free the canonical branch address while preserving the legacy endpoint row.
update radar.endpoints
set status = 'ARCHIVED',
    address = 'archived:bus/vera-sol-v1:lane-vera-sol',
    metadata = metadata || jsonb_build_object(
      'original_address', 'bus/vera-sol-v1',
      'superseded_by', 'lane-vera',
      'superseded_identity', 'vera'
    ),
    updated_at = now()
where endpoint_id = 'lane-vera-sol';

insert into radar.endpoints(endpoint_id, identity_id, transport, address, status, metadata)
values (
  'lane-vera',
  'vera',
  'github_branch',
  'bus/vera-sol-v1',
  'ACTIVE',
  jsonb_build_object(
    'role', 'sole_writer_mailbox_projection',
    'projection_basis', 'github_writer_lane_observed',
    'historical_branch_name', true,
    'liveness_claimed', false
  )
)
on conflict (endpoint_id) do update
set identity_id = excluded.identity_id,
    transport = excluded.transport,
    address = excluded.address,
    status = 'ACTIVE',
    metadata = radar.endpoints.metadata || excluded.metadata,
    updated_at = now();

update radar.identities
set lifecycle_status = 'ARCHIVED',
    metadata = metadata || jsonb_build_object(
      'superseded_by', 'vera',
      'superseded_reason', 'logical_identity_normalization',
      'historical_branch', 'bus/vera-sol-v1'
    ),
    updated_at = now()
where identity_id = 'vera-sol';

commit;
