begin;

do $$
declare
  test_id text := '__radar_live_projection_sql_test__';
  first_result text;
  second_result text;
  conflict_result text;
  stored_hash text;
begin
  delete from radar.reconciliation_events
  where code = 'MESSAGE_PROJECTION_CONFLICT'
    and detail->>'message_id' = test_id;
  delete from radar.messages where message_id = test_id;

  first_result := radar.project_bus_message_v1(
    test_id,
    '2026-09-02T20:00:00Z'::timestamptz,
    'radar',
    array['one'],
    false,
    array['github://test/one'],
    repeat('a', 64),
    'chat-bus:test:a',
    jsonb_build_object('subject','provider contract test','body_sha256',repeat('b',64))
  );
  if first_result <> 'INSERTED' then
    raise exception 'EXPECTED_INSERTED_GOT_%', first_result;
  end if;

  second_result := radar.project_bus_message_v1(
    test_id,
    '2026-09-02T20:00:00Z'::timestamptz,
    'radar',
    array['one'],
    false,
    array['github://test/one'],
    repeat('a', 64),
    'chat-bus:test:a',
    jsonb_build_object('subject','provider contract test','body_sha256',repeat('b',64))
  );
  if second_result <> 'IDEMPOTENT' then
    raise exception 'EXPECTED_IDEMPOTENT_GOT_%', second_result;
  end if;

  conflict_result := radar.project_bus_message_v1(
    test_id,
    '2026-09-02T20:00:00Z'::timestamptz,
    'radar',
    array['one'],
    false,
    array['github://test/two'],
    repeat('c', 64),
    'chat-bus:test:c',
    jsonb_build_object('subject','conflicting test','body_sha256',repeat('d',64))
  );
  if conflict_result <> 'CONFLICT' then
    raise exception 'EXPECTED_CONFLICT_GOT_%', conflict_result;
  end if;

  select content_hash into stored_hash from radar.messages where message_id = test_id;
  if stored_hash <> repeat('a', 64) then
    raise exception 'CONFLICT_OVERWROTE_CANONICAL_PROJECTION';
  end if;

  if not exists (
    select 1 from radar.reconciliation_events
    where code = 'MESSAGE_PROJECTION_CONFLICT'
      and detail->>'message_id' = test_id
      and detail->>'incoming_content_hash' = repeat('c', 64)
  ) then
    raise exception 'CONFLICT_RECONCILIATION_EVENT_MISSING';
  end if;

  if not exists (
    select 1 from pg_publication_tables
    where pubname='supabase_realtime' and schemaname='radar' and tablename='messages'
  ) then
    raise exception 'RADAR_MESSAGES_NOT_REALTIME';
  end if;

  if to_regclass('radar.identity_visuals') is not null and not exists (
    select 1 from pg_publication_tables
    where pubname='supabase_realtime' and schemaname='radar' and tablename='identity_visuals'
  ) then
    raise exception 'RADAR_IDENTITY_VISUALS_NOT_REALTIME';
  end if;
end
$$;

rollback;
