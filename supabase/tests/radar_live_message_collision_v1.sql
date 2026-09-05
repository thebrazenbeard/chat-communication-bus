begin;

do $$
declare
  test_id_base text := '__radar_collision_sql_test__';
  -- add a short random suffix so multiple runs won't collide
  test_suffix text := substring(md5(random()::text) from 1 for 8);
  test_id text := test_id_base || test_suffix;
  first_result text;
  conflict_result text;
  replay_result text;
  qualified_id text := test_id || '~' || substring(repeat('c', 64) from 1 for 16);
begin
  -- cleanup any pre-existing rows for these ids (this will be rolled back at the end)
  delete from radar.reconciliation_events
  where code = 'MESSAGE_PROJECTION_CONFLICT'
    and detail->>'message_id' = test_id;
  delete from radar.messages
  where message_id in (test_id, qualified_id);

  -- first, project the original message
  first_result := radar.project_bus_message_v1(
    test_id,
    timestamp with time zone '2026-09-02T20:00:00Z',
    'radar',
    array['one'],
    false,
    array['github://test/original'],
    repeat('a', 64),
    'chat-bus:test:original',
    jsonb_build_object('subject','original')
  );
  if first_result <> 'INSERTED' then
    raise exception 'EXPECTED INSERTED, GOT: %', first_result;
  end if;

  -- now project a colliding message (same declared id but different content_hash)
  conflict_result := radar.project_bus_message_v1(
    test_id,
    timestamp with time zone '2026-09-02T20:01:00Z',
    'radar',
    array['one'],
    false,
    array['github://test/collision'],
    repeat('c', 64),
    'chat-bus:test:collision',
    jsonb_build_object('subject','collision')
  );
  if conflict_result <> ('CONFLICT_INSERTED:' || qualified_id) then
    raise exception 'EXPECTED % BUT GOT %', 'CONFLICT_INSERTED:' || qualified_id, conflict_result;
  end if;

  -- verify original wasn't overwritten
  if (select content_hash from radar.messages where message_id = test_id) <> repeat('a', 64) then
    raise exception 'ORIGINAL_OVERWRITTEN: expected % for %', repeat('a',64), test_id;
  end if;

  -- verify qualified collision row exists with the new hash
  if (select content_hash from radar.messages where message_id = qualified_id) <> repeat('c', 64) then
    raise exception 'QUALIFIED_COLLISION_MISSING: expected % for %', repeat('c',64), qualified_id;
  end if;

  -- verify provenance declared_message_id preserved
  if (select payload->>'declared_message_id' from radar.messages where message_id = qualified_id) <> test_id then
    raise exception 'DECLARED_ID_PROVENANCE_MISSING: expected declared_message_id % for %', test_id, qualified_id;
  end if;

  -- verify collision marker is set on the qualified row
  if coalesce((select (payload->>'projection_collision')::boolean from radar.messages where message_id = qualified_id), false) is not true then
    raise exception 'COLLISION_MARKER_MISSING for %', qualified_id;
  end if;

  -- replay the same collision and ensure idempotent response
  replay_result := radar.project_bus_message_v1(
    test_id,
    timestamp with time zone '2026-09-02T20:01:00Z',
    'radar',
    array['one'],
    false,
    array['github://test/collision'],
    repeat('c', 64),
    'chat-bus:test:collision',
    jsonb_build_object('subject','collision')
  );
  if replay_result <> ('CONFLICT_IDEMPOTENT:' || qualified_id) then
    raise exception 'EXPECTED % BUT GOT %', 'CONFLICT_IDEMPOTENT:' || qualified_id, replay_result;
  end if;

  raise notice 'radar_live_message_collision_v1 passed for % and %', test_id, qualified_id;
end
$$;

rollback;
