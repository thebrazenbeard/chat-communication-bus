begin;

do $$
declare
  test_id text := '__radar_collision_sql_test__';
  first_result text;
  conflict_result text;
  replay_result text;
  qualified_id text := test_id || '~' || substring(repeat('c', 64) from 1 for 16);
begin
  delete from radar.reconciliation_events
  where code = 'MESSAGE_PROJECTION_CONFLICT'
    and detail->>'message_id' = test_id;
  delete from radar.messages where message_id = qualified_id;
  delete from radar.messages where message_id = test_id;

  first_result := radar.project_bus_message_v1(
    test_id,
    '2026-09-02T20:00:00Z'::timestamptz,
    'radar',
    array['one'],
    false,
    array['github://test/original'],
    repeat('a', 64),
    'chat-bus:test:original',
    jsonb_build_object('subject','original')
  );
  if first_result <> 'INSERTED' then
    raise exception 'EXPECTED_INSERTED_GOT_%', first_result;
  end if;

  conflict_result := radar.project_bus_message_v1(
    test_id,
    '2026-09-02T20:01:00Z'::timestamptz,
    'radar',
    array['one'],
    false,
    array['github://test/collision'],
    repeat('c', 64),
    'chat-bus:test:collision',
    jsonb_build_object('subject','collision')
  );
  if conflict_result <> 'CONFLICT_INSERTED:' || qualified_id then
    raise exception 'EXPECTED_CONFLICT_INSERTED_GOT_%', conflict_result;
  end if;

  if (select content_hash from radar.messages where message_id = test_id) <> repeat('a', 64) then
    raise exception 'ORIGINAL_OVERWRITTEN';
  end if;
  if (select content_hash from radar.messages where message_id = qualified_id) <> repeat('c', 64) then
    raise exception 'QUALIFIED_COLLISION_MISSING';
  end if;
  if (select payload->>'declared_message_id' from radar.messages where message_id = qualified_id) <> test_id then
    raise exception 'DECLARED_ID_PROVENANCE_MISSING';
  end if;
  if coalesce((select (payload->>'projection_collision')::boolean from radar.messages where message_id = qualified_id), false) is not true then
    raise exception 'COLLISION_MARKER_MISSING';
  end if;

  replay_result := radar.project_bus_message_v1(
    test_id,
    '2026-09-02T20:01:00Z'::timestamptz,
    'radar',
    array['one'],
    false,
    array['github://test/collision'],
    repeat('c', 64),
    'chat-bus:test:collision',
    jsonb_build_object('subject','collision')
  );
  if replay_result <> 'CONFLICT_IDEMPOTENT:' || qualified_id then
    raise exception 'EXPECTED_CONFLICT_IDEMPOTENT_GOT_%', replay_result;
  end if;
end
$$;

rollback;
