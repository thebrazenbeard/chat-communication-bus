begin;

do $$
/*
  Smoke test for radar.project_bus_message_v1

  Improvements in this version:
  - Use a unique test_id per run to avoid collisions in parallel test runs.
  - Defensive cleanup that targets the test prefix instead of an exact id.
  - Early explicit check for the function's existence.
  - Clearer exception messages including the test_id for easier debugging.
  - Final RAISE NOTICE on success.
*/
declare
  base_test_id constant text := '__radar_live_projection_sql_test__';
  -- make test_id unique so multiple CI jobs can run concurrently without interfering
  test_id text := base_test_id || '_' || substr(md5(clock_timestamp()::text || random()::text), 1, 8);
  first_result text;
  second_result text;
  conflict_result text;
  stored_hash text;
begin
  -- Defensive cleanup: only remove old test artifacts that share the test prefix.
  delete from radar.reconciliation_events
  where code = 'MESSAGE_PROJECTION_CONFLICT'
    and detail->>'message_id' like base_test_id || '%';
  delete from radar.messages where message_id like base_test_id || '%';

  -- Ensure the expected function exists in radar schema to fail fast with a clear message.
  if not exists (
    select 1
    from pg_proc p
    join pg_namespace n on p.pronamespace = n.oid
    where p.proname = 'project_bus_message_v1' and n.nspname = 'radar'
  ) then
    raise exception 'MISSING_FUNCTION radar.project_bus_message_v1 - ensure the migration that creates it has run';
  end if;

  -- First insert should return 'INSERTED'
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
    raise exception 'EXPECTED_INSERTED_GOT_% for test_id=%', first_result, test_id;
  end if;

  -- Same projection again should be idempotent
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
    raise exception 'EXPECTED_IDEMPOTENT_GOT_% for test_id=%', second_result, test_id;
  end if;

  -- Conflicting projection should return 'CONFLICT' and should not overwrite canonical content_hash
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
    raise exception 'EXPECTED_CONFLICT_GOT_% for test_id=%', conflict_result, test_id;
  end if;

  -- Verify canonical message wasn't overwritten
  select content_hash into stored_hash from radar.messages where message_id = test_id;
  if stored_hash <> repeat('a', 64) then
    raise exception 'CONFLICT_OVERWROTE_CANONICAL_PROJECTION for test_id=%', test_id;
  end if;

  -- Verify a reconciliation event was created referencing the incoming hash
  if not exists (
    select 1 from radar.reconciliation_events
    where code = 'MESSAGE_PROJECTION_CONFLICT'
      and detail->>'message_id' = test_id
      and detail->>'incoming_content_hash' = repeat('c', 64)
  ) then
    raise exception 'CONFLICT_RECONCILIATION_EVENT_MISSING for test_id=%', test_id;
  end if;

  -- Ensure messages are published to supabase_realtime
  if not exists (
    select 1 from pg_publication_tables
    where pubname='supabase_realtime' and schemaname='radar' and tablename='messages'
  ) then
    raise exception 'RADAR_MESSAGES_NOT_REALTIME - ensure supabase_realtime publication includes radar.messages';
  end if;

  -- identity_visuals is optional; if it exists the publication must include it
  if to_regclass('radar.identity_visuals') is not null and not exists (
    select 1 from pg_publication_tables
    where pubname='supabase_realtime' and schemaname='radar' and tablename='identity_visuals'
  ) then
    raise exception 'RADAR_IDENTITY_VISUALS_NOT_REALTIME - radar.identity_visuals exists but is not published to supabase_realtime';
  end if;

  raise notice 'radar.project_bus_message_v1 smoke test passed for %', test_id;
end
$$;

rollback;
