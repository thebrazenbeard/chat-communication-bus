-- Radar provider projection repair: replace the false-positive Hephaestus v1
-- endpoint projection with the clean administrative v2 writer mailbox.
--
-- GitHub remains canonical. `bus/hephaestus-v1` is preserved untouched as
-- malformed historical evidence. This repair performs no DELETE and does not
-- assert Hephaestus runtime/session liveness or author any Hephaestus message.

begin;

do $$
begin
  if not exists (
    select 1
    from radar.identities
    where identity_id = 'hephaestus'
  ) then
    raise exception 'RADAR_HEPHAESTUS_IDENTITY_MISSING';
  end if;

  if not exists (
    select 1
    from radar.endpoints
    where endpoint_id = 'lane-hephaestus'
      and identity_id = 'hephaestus'
      and transport = 'github_branch'
      and address in ('bus/hephaestus-v1', 'bus/hephaestus-v2')
  ) then
    raise exception 'RADAR_HEPHAESTUS_ENDPOINT_UNEXPECTED';
  end if;
end
$$;

update radar.identities
set metadata = metadata || jsonb_build_object(
      'projection_basis', 'github_writer_lane_structurally_valid',
      'observed_branch', 'bus/hephaestus-v2',
      'malformed_historical_branches', jsonb_build_array('bus/hephaestus-v1'),
      'liveness_claimed', false
    ),
    updated_at = now()
where identity_id = 'hephaestus';

update radar.endpoints
set address = 'bus/hephaestus-v2',
    status = 'ACTIVE',
    metadata = metadata || jsonb_build_object(
      'role', 'sole_writer_mailbox_projection',
      'projection_basis', 'github_writer_lane_structurally_valid',
      'malformed_historical_branch', 'bus/hephaestus-v1',
      'liveness_claimed', false
    ),
    updated_at = now()
where endpoint_id = 'lane-hephaestus'
  and identity_id = 'hephaestus'
  and transport = 'github_branch';

insert into radar.reconciliation_events(code, repair_class, source_ref, detail)
select
  'HEPHAESTUS_MALFORMED_LANE_REPAIRED',
  'SAFE_PROJECTION_REPAIR',
  'supabase/repairs/20260902_repair_hephaestus_lane_v2.sql',
  jsonb_build_object(
    'identity_id', 'hephaestus',
    'old_branch', 'bus/hephaestus-v1',
    'new_branch', 'bus/hephaestus-v2',
    'old_branch_preserved', true,
    'liveness_claimed', false
  )
where not exists (
  select 1
  from radar.reconciliation_events
  where code = 'HEPHAESTUS_MALFORMED_LANE_REPAIRED'
    and source_ref = 'supabase/repairs/20260902_repair_hephaestus_lane_v2.sql'
);

commit;
