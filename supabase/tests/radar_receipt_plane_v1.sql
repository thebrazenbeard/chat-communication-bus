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
  insert into radar.identities(identity_id, display_name, lifecycle_status, metadata)
  values
    ('receipt-test-one', 'Receipt Test One', 'ACTIVE', '{}'::jsonb),
    ('receipt-test-six', 'Receipt Test Six', 'ACTIVE', '{}'::jsonb)
  on conflict (identity_id) do nothing;

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    target_id, 1, '2026-09-02T20:00:00Z', 'receipt-test-one',
    array['receipt-test-six'], 'chat_bus', 'bus_message', 3, true,
    array['github://receipt-test/target'], repeat('a', 64),
    'receipt-test:target',
    jsonb_build_object('message_id', target_id, 'subject', 'target')
  );

  if not exists (
    select 1 from radar.delivery_events
    where message_id = target_id
      and identity_id = 'receipt-test-six'
      and event_type = 'PROJECTED_FOR_IDENTITY'
      and outcome = 'INDEXED_NOT_DELIVERED'
  ) then
    raise exception 'PROJECTED_FOR_IDENTITY_EVENT_MISSING';
  end if;

  if exists (
    select 1 from radar.acknowledgements
    where message_id = target_id and identity_id = 'receipt-test-six'
  ) then
    raise exception 'PROJECTION_FALSELY_CREATED_ACK';
  end if;

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    reply_id, 1, '2026-09-02T20:01:00Z', 'receipt-test-six',
    array['receipt-test-one'], 'chat_bus', 'bus_message', 3, false,
    array['github://receipt-test/reply'], repeat('b', 64),
    'receipt-test:reply',
    jsonb_build_object('message_id', reply_id, 'reply_to', target_id, 'subject', 'reply')
  );

  if not exists (
    select 1 from radar.acknowledgements
    where message_id = target_id
      and identity_id = 'receipt-test-six'
      and acknowledgement_type = 'READ'
      and evidence_ref = 'github://receipt-test/reply'
  ) then
    raise exception 'EXPLICIT_REPLY_READ_ACK_MISSING';
  end if;

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values
  (
    ambiguous_id, 1, '2026-09-02T20:02:00Z', 'receipt-test-one',
    array['receipt-test-six'], 'chat_bus', 'bus_message', 3, true,
    array['github://receipt-test/ambiguous-original'], repeat('c', 64),
    'receipt-test:ambiguous-original',
    jsonb_build_object('message_id', ambiguous_id, 'subject', 'ambiguous original')
  ),
  (
    qualified_id, 1, '2026-09-02T20:03:00Z', 'receipt-test-one',
    array['receipt-test-six'], 'chat_bus', 'bus_message', 3, true,
    array['github://receipt-test/ambiguous-qualified'], repeat('d', 64),
    'receipt-test:ambiguous-qualified',
    jsonb_build_object(
      'message_id', qualified_id,
      'declared_message_id', ambiguous_id,
      'projection_collision', true,
      'subject', 'ambiguous qualified'
    )
  );

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    ambiguous_reply_id, 1, '2026-09-02T20:04:00Z', 'receipt-test-six',
    array['receipt-test-one'], 'chat_bus', 'bus_message', 3, false,
    array['github://receipt-test/ambiguous-reply'], repeat('e', 64),
    'receipt-test:ambiguous-reply',
    jsonb_build_object('message_id', ambiguous_reply_id, 'reply_to', ambiguous_id)
  );

  if exists (
    select 1 from radar.acknowledgements
    where identity_id = 'receipt-test-six'
      and acknowledgement_type = 'READ'
      and message_id in (ambiguous_id, qualified_id)
  ) then
    raise exception 'AMBIGUOUS_REPLY_FALSELY_ACKNOWLEDGED';
  end if;

  if not exists (
    select 1 from radar.reconciliation_events
    where code = 'AMBIGUOUS_REPLY_REFERENCE'
      and detail->>'reply_message_id' = ambiguous_reply_id
      and detail->>'referenced_id' = ambiguous_id
      and detail->>'resolution' = 'no_read_acknowledgement_emitted'
  ) then
    raise exception 'AMBIGUOUS_REPLY_OBSERVATION_MISSING';
  end if;

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

  perform radar.reconcile_bus_receipts_v1();

  if projection_events_before <> (
    select count(*) from radar.delivery_events
    where message_id like 'receipt-test-%'
      and event_type = 'PROJECTED_FOR_IDENTITY'
  ) then
    raise exception 'PROJECTION_EVENTS_NOT_IDEMPOTENT';
  end if;

  if reads_before <> (
    select count(*) from radar.acknowledgements
    where message_id like 'receipt-test-%'
      and acknowledgement_type = 'READ'
  ) then
    raise exception 'READ_ACKS_NOT_IDEMPOTENT';
  end if;

  if ambiguities_before <> (
    select count(*) from radar.reconciliation_events
    where code = 'AMBIGUOUS_REPLY_REFERENCE'
      and detail->>'reply_message_id' = ambiguous_reply_id
  ) then
    raise exception 'AMBIGUITY_EVENTS_NOT_IDEMPOTENT';
  end if;
end
$$;

rollback;
