begin;

do $$
declare
  identity text := 'bridge-test';
  branch text := 'bus/bridge-test-v1';
  control_sha text := repeat('a', 40);
  topology_sha text := repeat('b', 40);
  target_sha text := repeat('c', 40);
  lane jsonb;
  batch jsonb;
  finalized jsonb;
  fn text;
begin
  -- These bridge functions remain service-role callable after the later atomic
  -- projection migration. Direct per-file result recording is intentionally
  -- excluded because atomic projection revokes that bypass.
  foreach fn in array array[
    'public.radar_projection_get_lane_v1(text,text)',
    'public.radar_projection_set_control_cut_v1(text,text,text,text)',
    'public.radar_projection_claim_batch_v1(text,text,text,text,text,text,text[],text,integer)',
    'public.radar_projection_finalize_batch_v1(uuid,uuid)'
  ] loop
    if has_function_privilege('anon', fn, 'EXECUTE') then
      raise exception 'ANON_EXECUTE_%', fn;
    end if;
    if has_function_privilege('authenticated', fn, 'EXECUTE') then
      raise exception 'AUTH_EXECUTE_%', fn;
    end if;
    if not has_function_privilege('service_role', fn, 'EXECUTE') then
      raise exception 'SERVICE_EXECUTE_MISSING_%', fn;
    end if;
  end loop;

  -- Cumulative contract after 20260908010500: service_role must not be able to
  -- independently mark a journal file successful, while the atomic projection
  -- bridge is the one service-role path that can project+record together.
  if has_function_privilege(
       'service_role',
       'public.radar_projection_record_file_result_v1(uuid,uuid,text,text,text)',
       'EXECUTE'
     ) then
    raise exception 'SERVICE_RECORD_FILE_RESULT_BYPASS_EXPOSED';
  end if;
  if has_function_privilege(
       'anon',
       'public.radar_projection_project_file_v1(uuid,uuid,text,text,timestamptz,text,text[],boolean,text[],text,text,jsonb)',
       'EXECUTE'
     )
     or has_function_privilege(
       'authenticated',
       'public.radar_projection_project_file_v1(uuid,uuid,text,text,timestamptz,text,text[],boolean,text[],text,text,jsonb)',
       'EXECUTE'
     ) then
    raise exception 'CLIENT_ATOMIC_PROJECT_EXECUTE_EXPOSED';
  end if;
  if not has_function_privilege(
       'service_role',
       'public.radar_projection_project_file_v1(uuid,uuid,text,text,timestamptz,text,text[],boolean,text[],text,text,jsonb)',
       'EXECUTE'
     ) then
    raise exception 'SERVICE_ATOMIC_PROJECT_EXECUTE_MISSING';
  end if;

  if to_regprocedure('public.radar_projection_seed_lane_v1(text,text,text)') is not null then
    raise exception 'SEED_MUST_NOT_BE_EXPOSED';
  end if;

  perform radar.projection_seed_lane_v1(identity, branch, null);
  select public.radar_projection_get_lane_v1(identity, branch) into lane;
  if lane is null or lane->>'projected_head_sha' is not null then
    raise exception 'EXPECTED_NULL_SEEDED_CURSOR_GOT_%', lane;
  end if;

  perform public.radar_projection_set_control_cut_v1(
    identity, branch, control_sha, topology_sha
  );
  select public.radar_projection_claim_batch_v1(
    identity,
    branch,
    null,
    target_sha,
    control_sha,
    topology_sha,
    array[]::text[],
    'bridge-test-owner',
    300
  ) into batch;

  if batch->>'batch_id' is null or batch->>'claim_token' is null then
    raise exception 'CLAIM_BRIDGE_INVALID_%', batch;
  end if;

  select public.radar_projection_finalize_batch_v1(
    (batch->>'batch_id')::uuid,
    (batch->>'claim_token')::uuid
  ) into finalized;
  if finalized->>'projected_head_sha' <> target_sha then
    raise exception 'FINALIZE_BRIDGE_INVALID_%', finalized;
  end if;
end;
$$;

rollback;
