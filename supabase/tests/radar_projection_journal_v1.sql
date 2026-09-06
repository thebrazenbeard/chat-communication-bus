-- Run after applying 20260906154101_radar_projection_journal_v1.sql.
-- All fixture writes roll back; assertions fail loudly.

begin;

do $$
declare
  batch radar.projection_batches;
  takeover radar.projection_batches;
  lane radar.projection_lane_state;
  control_a constant text := 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
  control_b constant text := 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
  topology_a constant text := 'cccccccccccccccccccccccccccccccccccccccc';
  head_0 constant text := '0000000000000000000000000000000000000000';
  head_1 constant text := '1111111111111111111111111111111111111111';
  head_2 constant text := '2222222222222222222222222222222222222222';
  head_3 constant text := '3333333333333333333333333333333333333333';
  head_4 constant text := '4444444444444444444444444444444444444444';
begin
  -- Claims never invent lane state, even for an uninitialized cursor.
  begin
    perform radar.projection_claim_batch_v1(
      'journal-unseeded', 'bus/journal-unseeded', null, head_0,
      control_a, topology_a, array[]::text[], 'worker-a', 300
    );
    raise exception 'RADAR_TEST_EXPECTED_LANE_UNSEEDED';
  exception
    when check_violation then
      if sqlerrm not like '%RADAR_PROJECTION_LANE_UNSEEDED%' then
        raise;
      end if;
  end;

  -- Explicit NULL seed + control cut permits a zero-file activation-anchor finalize.
  perform radar.projection_seed_lane_v1('journal-bootstrap', 'bus/journal-bootstrap', null);
  perform radar.projection_set_control_cut_v1(
    'journal-bootstrap', 'bus/journal-bootstrap', control_a, topology_a
  );
  select * into batch from radar.projection_claim_batch_v1(
    'journal-bootstrap', 'bus/journal-bootstrap', null, head_0,
    control_a, topology_a, array[]::text[], 'worker-a', 300
  );
  select * into lane from radar.projection_finalize_batch_v1(batch.batch_id, batch.claim_token);
  if lane.projected_head_sha <> head_0 then
    raise exception 'RADAR_BOOTSTRAP_CURSOR_NOT_ADVANCED';
  end if;

  -- A normal batch cannot finalize until every file is PROJECTED/IDEMPOTENT.
  perform radar.projection_seed_lane_v1('journal-normal', 'bus/journal-normal', head_1);
  perform radar.projection_set_control_cut_v1(
    'journal-normal', 'bus/journal-normal', control_a, topology_a
  );
  select * into batch from radar.projection_claim_batch_v1(
    'journal-normal', 'bus/journal-normal', head_1, head_2,
    control_a, topology_a,
    array['messages/journal-0001.md','messages/journal-0002.md'],
    'worker-a', 300
  );
  perform radar.projection_record_file_result_v1(
    batch.batch_id, batch.claim_token, 'messages/journal-0001.md', 'PROJECTED', 'provider:1'
  );
  begin
    perform radar.projection_finalize_batch_v1(batch.batch_id, batch.claim_token);
    raise exception 'RADAR_TEST_EXPECTED_UNRESOLVED_FILES';
  exception
    when check_violation then
      if sqlerrm not like '%RADAR_PROJECTION_UNRESOLVED_FILES%' then
        raise;
      end if;
  end;
  if (select projected_head_sha from radar.projection_lane_state
      where identity_id='journal-normal' and branch='bus/journal-normal') <> head_1 then
    raise exception 'RADAR_UNRESOLVED_BATCH_MOVED_CURSOR';
  end if;
  perform radar.projection_record_file_result_v1(
    batch.batch_id, batch.claim_token, 'messages/journal-0002.md', 'IDEMPOTENT', 'provider:2'
  );
  perform radar.projection_finalize_batch_v1(batch.batch_id, batch.claim_token);
  perform radar.projection_finalize_batch_v1(batch.batch_id, batch.claim_token);
  if (select projected_head_sha from radar.projection_lane_state
      where identity_id='journal-normal' and branch='bus/journal-normal') <> head_2 then
    raise exception 'RADAR_COMPLETE_BATCH_CURSOR_INCORRECT';
  end if;

  -- An expired claim is fenced; a takeover can proceed and the stale token stays dead.
  perform radar.projection_seed_lane_v1('journal-takeover', 'bus/journal-takeover', head_2);
  perform radar.projection_set_control_cut_v1(
    'journal-takeover', 'bus/journal-takeover', control_a, topology_a
  );
  select * into batch from radar.projection_claim_batch_v1(
    'journal-takeover', 'bus/journal-takeover', head_2, head_3,
    control_a, topology_a, array['messages/takeover.md'], 'worker-a', 300
  );
  update radar.projection_batches
  set claim_expires_at = now() - interval '1 second'
  where batch_id = batch.batch_id;
  begin
    perform radar.projection_finalize_batch_v1(batch.batch_id, batch.claim_token);
    raise exception 'RADAR_TEST_EXPECTED_STALE_CLAIM';
  exception
    when sqlstate '40001' then
      if sqlerrm not like '%RADAR_PROJECTION_STALE_CLAIM%' then
        raise;
      end if;
  end;

  select * into takeover from radar.projection_claim_batch_v1(
    'journal-takeover', 'bus/journal-takeover', head_2, head_3,
    control_a, topology_a, array['messages/takeover.md'], 'worker-b', 300
  );
  begin
    perform radar.projection_record_file_result_v1(
      batch.batch_id, batch.claim_token, 'messages/takeover.md', 'PROJECTED', null
    );
    raise exception 'RADAR_TEST_EXPECTED_STALE_FILE_WRITER';
  exception
    when sqlstate '40001' then
      if sqlerrm not like '%RADAR_PROJECTION_STALE_CLAIM%' then
        raise;
      end if;
  end;
  perform radar.projection_record_file_result_v1(
    takeover.batch_id, takeover.claim_token, 'messages/takeover.md', 'PROJECTED', null
  );
  perform radar.projection_finalize_batch_v1(takeover.batch_id, takeover.claim_token);

  -- A control/topology cut change fences a worker even after its last file succeeds.
  perform radar.projection_seed_lane_v1('journal-control', 'bus/journal-control', head_3);
  perform radar.projection_set_control_cut_v1(
    'journal-control', 'bus/journal-control', control_a, topology_a
  );
  select * into batch from radar.projection_claim_batch_v1(
    'journal-control', 'bus/journal-control', head_3, head_4,
    control_a, topology_a, array['messages/control.md'], 'worker-a', 300
  );
  perform radar.projection_record_file_result_v1(
    batch.batch_id, batch.claim_token, 'messages/control.md', 'PROJECTED', null
  );
  perform radar.projection_set_control_cut_v1(
    'journal-control', 'bus/journal-control', control_b, topology_a
  );
  begin
    perform radar.projection_finalize_batch_v1(batch.batch_id, batch.claim_token);
    raise exception 'RADAR_TEST_EXPECTED_CONTROL_CUT_CHANGED';
  exception
    when sqlstate '40001' then
      if sqlerrm not like '%RADAR_PROJECTION_CONTROL_CUT_CHANGED%' then
        raise;
      end if;
  end;
  if (select projected_head_sha from radar.projection_lane_state
      where identity_id='journal-control' and branch='bus/journal-control') <> head_3 then
    raise exception 'RADAR_CONTROL_CHANGE_MOVED_CURSOR';
  end if;
end
$$;

-- The service role may read journal state but cannot bypass fencing with table DML.
do $$
begin
  if has_table_privilege('service_role', 'radar.projection_lane_state', 'INSERT')
     or has_table_privilege('service_role', 'radar.projection_lane_state', 'UPDATE')
     or has_table_privilege('service_role', 'radar.projection_batches', 'INSERT')
     or has_table_privilege('service_role', 'radar.projection_batches', 'UPDATE')
     or has_table_privilege('service_role', 'radar.projection_batch_files', 'INSERT')
     or has_table_privilege('service_role', 'radar.projection_batch_files', 'UPDATE') then
    raise exception 'RADAR_PROJECTION_DIRECT_WRITE_EXPOSED';
  end if;

  if not has_table_privilege('service_role', 'radar.projection_lane_state', 'SELECT') then
    raise exception 'RADAR_PROJECTION_SERVICE_READBACK_MISSING';
  end if;
end
$$;

-- Client roles cannot execute any journal mutation RPC.
do $$
declare
  sig text;
begin
  foreach sig in array array[
    'radar.projection_seed_lane_v1(text,text,text)',
    'radar.projection_set_control_cut_v1(text,text,text,text)',
    'radar.projection_claim_batch_v1(text,text,text,text,text,text,text[],text,integer)',
    'radar.projection_record_file_result_v1(uuid,uuid,text,text,text)',
    'radar.projection_finalize_batch_v1(uuid,uuid)'
  ]
  loop
    if has_function_privilege('anon', sig, 'EXECUTE')
       or has_function_privilege('authenticated', sig, 'EXECUTE') then
      raise exception 'RADAR_PROJECTION_RPC_EXECUTE_EXPOSED:%', sig;
    end if;
    if not has_function_privilege('service_role', sig, 'EXECUTE') then
      raise exception 'RADAR_PROJECTION_SERVICE_EXECUTE_MISSING:%', sig;
    end if;
  end loop;
end
$$;

rollback;
