-- Test: radar.reconcile_bus_receipts_v1()
-- Ensures explicit reply -> read ack creation and ambiguous-reply reconciliation,
-- and that reconcile is idempotent when re-run.
-- The script runs inside a transaction and uses ROLLBACK at the end so it leaves no state.
begin;

do $$
declare
  target_id text := 'receipt-test-one-0001';
  reply_id text := 'receipt-test-six-0001';
  ambiguous_id text := 'receipt-test-dup-0001';
  qualified_id text := 'receipt-test-dup-0001~aaaaaaaaaaaaaaaa';
  ambiguous_reply_id text := 'receipt-test-six-0002';
  projection_events_before integer;
  reads_before integer;
  ambiguities_before integer;
begin
  -- Clean up any leftover test data so this script is re-runnable.
  -- NOTE: tests should run against an isolated/test DB; these deletes scope by test prefix.
  delete from radar.reconciliation_events
    where code = 'AMBIGUOUS_REPLY_REFERENCE'
      and (detail->>'reply_message_id') like 'receipt-test-%';
  delete from radar.acknowledgements
    where (message_id like 'receipt-test-%' or identity_id like 'receipt-test-%');
  delete from radar.delivery_events
    where message_id like 'receipt-test-%';
  delete from radar.messages
    where message_id like 'receipt-test-%'
       or (payload->>'declared_message_id') like 'receipt-test-%';
  delete from radar.identities
    where identity_id in ('receipt-test-one','receipt-test-six');

  -- Create identities (idempotent)
  insert into radar.identities(identity_id, display_name, lifecycle_status, metadata)
  values
    ('receipt-test-one', 'Receipt Test One', 'ACTIVE', '{}'::jsonb),
    ('receipt-test-six', 'Receipt Test Six', 'ACTIVE', '{}'::jsonb)
  on conflict (identity_id) do nothing;

  -- Insert the target message (idempotent)
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    target_id, 1, '2026-09-02T20:00:00Z'::timestamptz, 'receipt-test-one',
    array['receipt-test-six'], 'chat_bus', 'bus_message', 3, true,
    array['github://receipt-test/target'], repeat('a', 64),
    'receipt-test:target',
    jsonb_build_object('message_id', target_id, 'subject', 'target')
  )
  on conflict (message_id) do nothing;

  -- Validate projection event recorded for target -> identity
  if not exists (
    select 1 from radar.delivery_events
    where message_id = target_id
      and identity_id = 'receipt-test-six'
      and event_type = 'PROJECTED_FOR_IDENTITY'
      and outcome = 'INDEXED_NOT_DELIVERED'
  ) then
    raise exception 'PROJECTED_FOR_IDENTITY_EVENT_MISSING for message=% identity=%', target_id, 'receipt-test-six';
  end if;

  -- Ensure no read acknowledgement exists prematurely
  if exists (
    select 1 from radar.acknowledgements
    where message_id = target_id and identity_id = 'receipt-test-six'
  ) then
    raise exception 'PROJECTION_FALSELY_CREATED_ACK for message=% identity=%', target_id, 'receipt-test-six';
  end if;

  -- Insert an explicit reply which should generate a READ acknowledgement for target
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    reply_id, 1, '2026-09-02T20:01:00Z'::timestamptz, 'receipt-test-six',
    array['receipt-test-one'], 'chat_bus', 'bus_message', 3, false,
    array['github://receipt-test/reply'], repeat('b', 64),
    'receipt-test:reply',
    jsonb_build_object('message_id', reply_id, 'reply_to', target_id, 'subject', 'reply')
  )
  on conflict (message_id) do nothing;

  if not exists (
    select 1 from radar.acknowledgements
    where message_id = target_id
      and identity_id = 'receipt-test-six'
      and acknowledgement_type = 'READ'
      and evidence_ref = 'github://receipt-test/reply'
  ) then
    raise exception 'EXPLICIT_REPLY_READ_ACK_MISSING: expected READ ack for target=% evidence=%', target_id, 'github://receipt-test/reply';
  end if;

  -- Insert ambiguous original + qualified projection (qualified declares the same message id)
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values
  (
    ambiguous_id, 1, '2026-09-02T20:02:00Z'::timestamptz, 'receipt-test-one',
    array['receipt-test-six'], 'chat_bus', 'bus_message', 3, true,
    array['github://receipt-test/ambiguous-original'], repeat('c', 64),
    'receipt-test:ambiguous-original',
    jsonb_build_object('message_id', ambiguous_id, 'subject', 'ambiguous original')
  )
  on conflict (message_id) do nothing;

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    qualified_id, 1, '2026-09-02T20:03:00Z'::timestamptz, 'receipt-test-one',
    array['receipt-test-six'], 'chat_bus', 'bus_message', 3, true,
    array['github://receipt-test/ambiguous-qualified'], repeat('d', 64),
    'receipt-test:ambiguous-qualified',
    jsonb_build_object(
      'message_id', qualified_id,
      'declared_message_id', ambiguous_id,
      'projection_collision', true,
      'subject', 'ambiguous qualified'
    )
  )
  on conflict (message_id) do nothing;

  -- Insert ambiguous reply referring to ambiguous original (should not create a READ ack due to ambiguity)
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    ambiguous_reply_id, 1, '2026-09-02T20:04:00Z'::timestamptz, 'receipt-test-six',
    array['receipt-test-one'], 'chat_bus', 'bus_message', 3, false,
    array['github://receipt-test/ambiguous-reply'], repeat('e', 64),
    'receipt-test:ambiguous-reply',
    jsonb_build_object('message_id', ambiguous_reply_id, 'reply_to', ambiguous_id)
  )
  on conflict (message_id) do nothing;

  if exists (
    select 1 from radar.acknowledgements
    where identity_id = 'receipt-test-six'
      and acknowledgement_type = 'READ'
      and message_id in (ambiguous_id, qualified_id)
  ) then
    raise exception 'AMBIGUOUS_REPLY_FALSELY_ACKNOWLEDGED for ambiguous ids (% , %)', ambiguous_id, qualified_id;
  end if;

  if not exists (
    select 1 from radar.reconciliation_events
    where code = 'AMBIGUOUS_REPLY_REFERENCE'
      and detail->>'reply_message_id' = ambiguous_reply_id
      and detail->>'referenced_id' = ambiguous_id
      and detail->>'resolution' = 'no_read_acknowledgement_emitted'
  ) then
    raise exception 'AMBIGUOUS_REPLY_OBSERVATION_MISSING for reply=% referenced=%', ambiguous_reply_id, ambiguous_id;
  end if;

  -- Capture counts so we can assert idempotency after reconcile.
  select count(*) into projection_events_before
  from radar.delivery_events
  where message_id like 'receipt-test-%'
    and event_type = 'PROJECTED_FOR_IDENTITY';

  select count(*) into reads_before
  from radar.acknowledgements
  where message_id like 'receipt-test-%'
    and acknowledgement_type = 'READ';

  select count(*) into ambiguities_before
  from radar.reconciliation_events
  where code = 'AMBIGUOUS_REPLY_REFERENCE'
    and detail->>'reply_message_id' = ambiguous_reply_id;

  -- Run the function under test
  perform radar.reconcile_bus_receipts_v1();

  -- Verify that reconcile is idempotent: the relevant counts did not change
  if projection_events_before <> (
    select count(*) from radar.delivery_events
    where message_id like 'receipt-test-%'
      and event_type = 'PROJECTED_FOR_IDENTITY'
  ) then
    raise exception 'PROJECTION_EVENTS_NOT_IDEMPOTENT: before=% after=%',
      projection_events_before,
      (select count(*) from radar.delivery_events where message_id like 'receipt-test-%' and event_type = 'PROJECTED_FOR_IDENTITY');
  end if;

  if reads_before <> (
    select count(*) from radar.acknowledgements
    where message_id like 'receipt-test-%'
      and acknowledgement_type = 'READ'
  ) then
    raise exception 'READ_ACKS_NOT_IDEMPOTENT: before=% after=%',
      reads_before,
      (select count(*) from radar.acknowledgements where message_id like 'receipt-test-%' and acknowledgement_type = 'READ');
  end if;

  if ambiguities_before <> (
    select count(*) from radar.reconciliation_events
    where code = 'AMBIGUOUS_REPLY_REFERENCE'
      and detail->>'reply_message_id' = ambiguous_reply_id
  ) then
    raise exception 'AMBIGUITY_EVENTS_NOT_IDEMPOTENT: before=% after=%',
      ambiguities_before,
      (select count(*) from radar.reconciliation_events where code = 'AMBIGUOUS_REPLY_REFERENCE' and detail->>'reply_message_id' = ambiguous_reply_id);
  end if;

  raise notice 'radar.reconcile_bus_receipts_v1 test passed for prefix receipt-test-*';
end
$$;

rollback;
