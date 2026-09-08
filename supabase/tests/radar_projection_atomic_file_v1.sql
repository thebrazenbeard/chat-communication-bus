-- Run after applying the Radar projection atomic-file hardening migration.
-- All fixture writes roll back; assertions fail loudly.

begin;

do $$
declare
  batch radar.projection_batches;
  lane radar.projection_lane_state;
  result text;
  control_a constant text := 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
  topology_a constant text := 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
  head_0 constant text := '0000000000000000000000000000000000000000';
  head_1 constant text := '1111111111111111111111111111111111111111';
  hash_expired constant text := 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
  hash_wrong_path constant text := 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
  hash_good constant text := 'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc';
begin
  -- An expired claim must be rejected before any message/reconciliation mutation.
  perform radar.projection_seed_lane_v1('atomic-expired', 'bus/atomic-expired', head_0);
  perform radar.projection_set_control_cut_v1(
    'atomic-expired', 'bus/atomic-expired', control_a, topology_a
  );
  select * into batch from radar.projection_claim_batch_v1(
    'atomic-expired', 'bus/atomic-expired', head_0, head_1,
    control_a, topology_a, array['messages/atomic-expired.md'], 'worker-a', 300
  );
  update radar.projection_batches
  set claim_expires_at = now() - interval '1 second'
  where batch_id = batch.batch_id;

  begin
    perform radar.projection_project_file_v1(
      batch.batch_id,
      batch.claim_token,
      'messages/atomic-expired.md',
      'atomic-expired-msg',
      now(),
      'atomic-expired',
      array['radar'],
      false,
      array['github://atomic-expired'],
      hash_expired,
      'chat-bus:atomic-expired-msg:' || hash_expired,
      jsonb_build_object(
        'admitted_lane_identity', 'atomic-expired',
        'source_path', 'messages/atomic-expired.md',
        'source_branch_head', head_1
      )
    );
    raise exception 'RADAR_TEST_EXPECTED_ATOMIC_STALE_CLAIM';
  exception
    when sqlstate '40001' then
      if sqlerrm not like '%RADAR_PROJECTION_STALE_CLAIM%' then
        raise;
      end if;
  end;

  if exists (select 1 from radar.messages where message_id = 'atomic-expired-msg') then
    raise exception 'RADAR_STALE_CLAIM_MUTATED_MESSAGES';
  end if;
  if (select state from radar.projection_batch_files
      where batch_id = batch.batch_id and path = 'messages/atomic-expired.md') <> 'PENDING' then
    raise exception 'RADAR_STALE_CLAIM_MUTATED_FILE_STATE';
  end if;

  -- A path not claimed by the batch must fail before message mutation.
  perform radar.projection_seed_lane_v1('atomic-path', 'bus/atomic-path', head_0);
  perform radar.projection_set_control_cut_v1(
    'atomic-path', 'bus/atomic-path', control_a, topology_a
  );
  select * into batch from radar.projection_claim_batch_v1(
    'atomic-path', 'bus/atomic-path', head_0, head_1,
    control_a, topology_a, array['messages/atomic-claimed.md'], 'worker-a', 300
  );

  begin
    perform radar.projection_project_file_v1(
      batch.batch_id,
      batch.claim_token,
      'messages/atomic-unclaimed.md',
      'atomic-wrong-path-msg',
      now(),
      'atomic-path',
      array['radar'],
      false,
      array['github://atomic-path'],
      hash_wrong_path,
      'chat-bus:atomic-wrong-path-msg:' || hash_wrong_path,
      jsonb_build_object(
        'admitted_lane_identity', 'atomic-path',
        'source_path', 'messages/atomic-unclaimed.md',
        'source_branch_head', head_1
      )
    );
    raise exception 'RADAR_TEST_EXPECTED_ATOMIC_UNKNOWN_PATH';
  exception
    when no_data_found then
      if sqlerrm not like '%RADAR_PROJECTION_FILE_UNKNOWN%' then
        raise;
      end if;
  end;

  if exists (select 1 from radar.messages where message_id = 'atomic-wrong-path-msg') then
    raise exception 'RADAR_UNCLAIMED_PATH_MUTATED_MESSAGES';
  end if;

  -- A valid active claim projects and journals one file in one transaction.
  perform radar.projection_seed_lane_v1('atomic-good', 'bus/atomic-good', head_0);
  perform radar.projection_set_control_cut_v1(
    'atomic-good', 'bus/atomic-good', control_a, topology_a
  );
  select * into batch from radar.projection_claim_batch_v1(
    'atomic-good', 'bus/atomic-good', head_0, head_1,
    control_a, topology_a, array['messages/atomic-good.md'], 'worker-a', 300
  );

  result := radar.projection_project_file_v1(
    batch.batch_id,
    batch.claim_token,
    'messages/atomic-good.md',
    'atomic-good-msg',
    now(),
    'atomic-good',
    array['radar'],
    false,
    array['github://atomic-good'],
    hash_good,
    'chat-bus:atomic-good-msg:' || hash_good,
    jsonb_build_object(
      'admitted_lane_identity', 'atomic-good',
      'source_path', 'messages/atomic-good.md',
      'source_branch_head', head_1
    )
  );
  if result <> 'INSERTED' then
    raise exception 'RADAR_ATOMIC_PROJECT_UNEXPECTED_RESULT:%', result;
  end if;
  if not exists (
    select 1 from radar.messages
    where message_id = 'atomic-good-msg' and content_hash = hash_good
  ) then
    raise exception 'RADAR_ATOMIC_PROJECT_MESSAGE_MISSING';
  end if;
  if not exists (
    select 1 from radar.projection_batch_files
    where batch_id = batch.batch_id
      and path = 'messages/atomic-good.md'
      and state = 'PROJECTED'
      and result_ref = 'INSERTED'
  ) then
    raise exception 'RADAR_ATOMIC_PROJECT_JOURNAL_MISSING';
  end if;

  -- Retrying the same successfully journaled file is an idempotent readback,
  -- not a second message mutation.
  result := radar.projection_project_file_v1(
    batch.batch_id,
    batch.claim_token,
    'messages/atomic-good.md',
    'atomic-good-msg',
    now(),
    'atomic-good',
    array['radar'],
    false,
    array['github://atomic-good'],
    hash_good,
    'chat-bus:atomic-good-msg:' || hash_good,
    jsonb_build_object(
      'admitted_lane_identity', 'atomic-good',
      'source_path', 'messages/atomic-good.md',
      'source_branch_head', head_1
    )
  );
  if result <> 'INSERTED' then
    raise exception 'RADAR_ATOMIC_PROJECT_RETRY_CHANGED_RESULT:%', result;
  end if;
  if (select count(*) from radar.messages where message_id = 'atomic-good-msg') <> 1 then
    raise exception 'RADAR_ATOMIC_PROJECT_RETRY_DUPLICATED_MESSAGE';
  end if;

  select * into lane from radar.projection_finalize_batch_v1(batch.batch_id, batch.claim_token);
  if lane.projected_head_sha <> head_1 then
    raise exception 'RADAR_ATOMIC_PROJECT_CURSOR_NOT_ADVANCED';
  end if;
end
$$;

-- The service key must not be able to bypass the journal by projecting a
-- message directly or by independently marking a claimed file successful.
do $$
begin
  if has_function_privilege(
       'service_role',
       'radar.project_bus_message_v1(text,timestamptz,text,text[],boolean,text[],text,text,jsonb)',
       'EXECUTE'
     )
     or has_function_privilege(
       'service_role',
       'public.radar_project_bus_message_v1(text,timestamptz,text,text[],boolean,text[],text,text,jsonb)',
       'EXECUTE'
     )
     or has_function_privilege(
       'service_role',
       'radar.projection_record_file_result_v1(uuid,uuid,text,text,text)',
       'EXECUTE'
     )
     or has_function_privilege(
       'service_role',
       'public.radar_projection_record_file_result_v1(uuid,uuid,text,text,text)',
       'EXECUTE'
     ) then
    raise exception 'RADAR_ATOMIC_PROJECTION_BYPASS_EXPOSED';
  end if;

  if not has_function_privilege(
       'service_role',
       'public.radar_projection_project_file_v1(uuid,uuid,text,text,timestamptz,text,text[],boolean,text[],text,text,jsonb)',
       'EXECUTE'
     ) then
    raise exception 'RADAR_ATOMIC_PROJECTION_SERVICE_EXECUTE_MISSING';
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
    raise exception 'RADAR_ATOMIC_PROJECTION_CLIENT_EXECUTE_EXPOSED';
  end if;
end
$$;

rollback;
