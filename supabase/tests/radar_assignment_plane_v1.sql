begin;

do $$
declare
  assignment_id_value text := '__radar_assignment_test__';
  root_message text := '__radar_assignment_root__';
  ack_message text := '__radar_assignment_ack__';
  fork_message text := '__radar_assignment_fork__';
  pending_message text := '__radar_assignment_pending__';
  invalid_message text := '__radar_assignment_invalid__';
  ordinary_message text := '__radar_assignment_ordinary__';
  root_event bigint;
  ack_event bigint;
  event_count_before integer;
  reconciliation_count_before integer;
begin
  insert into radar.identities(identity_id, display_name, lifecycle_status, metadata)
  values
    ('assignment-test-coordinator', 'Assignment Test Coordinator', 'ACTIVE', '{}'::jsonb),
    ('assignment-test-worker', 'Assignment Test Worker', 'ACTIVE', '{}'::jsonb)
  on conflict (identity_id) do nothing;

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    ordinary_message, 1, '2026-09-03T00:00:00Z', 'assignment-test-coordinator',
    array['assignment-test-worker'], 'chat_bus', 'bus_message', 3, false,
    array['github://assignment-test/ordinary'], repeat('0', 64),
    'assignment-test:ordinary',
    jsonb_build_object('subject', 'ordinary message')
  );

  if exists (select 1 from radar.assignments where assignment_id = assignment_id_value) then
    raise exception 'ORDINARY_MESSAGE_CREATED_ASSIGNMENT';
  end if;

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    root_message, 1, '2026-09-03T00:01:00Z', 'assignment-test-coordinator',
    array['assignment-test-worker'], 'chat_bus', 'bus_message', 3, true,
    array['github://assignment-test/root'], repeat('1', 64),
    'assignment-test:root',
    jsonb_build_object(
      'subject', 'explicit assignment root',
      'assignment_id', assignment_id_value,
      'assignment_workflow_id', 'assignment-test-workflow',
      'assignment_assignee', 'assignment-test-worker',
      'assignment_event', 'ASSIGNED',
      'assignment_state', 'ASSIGNED',
      'assignment_protected_authority', 'false'
    )
  );

  if not exists (
    select 1 from radar.assignments
    where assignment_id = assignment_id_value
      and workflow_id = 'assignment-test-workflow'
      and current_state = 'ASSIGNED'
      and assignee_identity_id = 'assignment-test-worker'
      and source_message_id = root_message
      and protected_authority = false
  ) then
    raise exception 'ASSIGNMENT_ROOT_NOT_PROJECTED';
  end if;

  select event_id into root_event
  from radar.assignment_events
  where assignment_id = assignment_id_value and operation_id = root_message;

  if root_event is null then
    raise exception 'ASSIGNMENT_ROOT_EVENT_MISSING';
  end if;

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    ack_message, 1, '2026-09-03T00:02:00Z', 'assignment-test-worker',
    array['assignment-test-coordinator'], 'chat_bus', 'bus_message', 3, false,
    array['github://assignment-test/ack'], repeat('2', 64),
    'assignment-test:ack',
    jsonb_build_object(
      'subject', 'assignment acknowledged',
      'assignment_id', assignment_id_value,
      'assignment_workflow_id', 'assignment-test-workflow',
      'assignment_assignee', 'assignment-test-worker',
      'assignment_event', 'ACKNOWLEDGED',
      'assignment_state', 'ACKNOWLEDGED',
      'assignment_predecessor_message_id', root_message,
      'assignment_protected_authority', 'false'
    )
  );

  select event_id into ack_event
  from radar.assignment_events
  where assignment_id = assignment_id_value and operation_id = ack_message;

  if ack_event is null then
    raise exception 'ASSIGNMENT_ACK_EVENT_MISSING';
  end if;

  if not exists (
    select 1 from radar.assignment_events
    where event_id = ack_event
      and predecessor_event_id = root_event
      and from_state = 'ASSIGNED'
      and to_state = 'ACKNOWLEDGED'
      and actor = 'assignment-test-worker'
      and receipt_sha256 = repeat('2', 64)
  ) then
    raise exception 'ASSIGNMENT_ACK_EVENT_BAD_RECEIPT';
  end if;

  if not exists (
    select 1 from radar.assignments
    where assignment_id = assignment_id_value
      and current_state = 'ACKNOWLEDGED'
      and current_event_id = ack_event
  ) then
    raise exception 'ASSIGNMENT_CURRENT_STATE_NOT_ADVANCED';
  end if;

  -- A stale fork naming the root after ACKNOWLEDGED must not advance state.
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    fork_message, 1, '2026-09-03T00:03:00Z', 'assignment-test-worker',
    array['assignment-test-coordinator'], 'chat_bus', 'bus_message', 3, false,
    array['github://assignment-test/fork'], repeat('3', 64),
    'assignment-test:fork',
    jsonb_build_object(
      'assignment_id', assignment_id_value,
      'assignment_workflow_id', 'assignment-test-workflow',
      'assignment_assignee', 'assignment-test-worker',
      'assignment_event', 'RUNNING',
      'assignment_state', 'RUNNING',
      'assignment_predecessor_message_id', root_message,
      'assignment_protected_authority', 'false'
    )
  );

  if exists (
    select 1 from radar.assignment_events
    where assignment_id = assignment_id_value and operation_id = fork_message
  ) then
    raise exception 'STALE_FORK_ADVANCED_ASSIGNMENT';
  end if;

  if not exists (
    select 1 from radar.reconciliation_events
    where code = 'ASSIGNMENT_EVENT_CONFLICT'
      and detail->>'message_id' = fork_message
      and detail->>'reason' = 'predecessor_is_not_current_assignment_event'
  ) then
    raise exception 'STALE_FORK_CONFLICT_OBSERVATION_MISSING';
  end if;

  -- A successor whose predecessor is not present remains pending.
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    pending_message, 1, '2026-09-03T00:04:00Z', 'assignment-test-worker',
    array['assignment-test-coordinator'], 'chat_bus', 'bus_message', 3, false,
    array['github://assignment-test/pending'], repeat('4', 64),
    'assignment-test:pending',
    jsonb_build_object(
      'assignment_id', '__radar_assignment_pending_chain__',
      'assignment_workflow_id', 'assignment-test-workflow',
      'assignment_assignee', 'assignment-test-worker',
      'assignment_event', 'RUNNING',
      'assignment_state', 'RUNNING',
      'assignment_predecessor_message_id', '__missing_assignment_predecessor__',
      'assignment_protected_authority', 'false'
    )
  );

  if not exists (
    select 1 from radar.reconciliation_events
    where code = 'ASSIGNMENT_EVENT_PENDING_PREDECESSOR'
      and detail->>'message_id' = pending_message
  ) then
    raise exception 'PENDING_PREDECESSOR_OBSERVATION_MISSING';
  end if;

  -- An explicit but incomplete assignment envelope is observed, not guessed.
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    invalid_message, 1, '2026-09-03T00:05:00Z', 'assignment-test-coordinator',
    array['assignment-test-worker'], 'chat_bus', 'bus_message', 3, false,
    array['github://assignment-test/invalid'], repeat('5', 64),
    'assignment-test:invalid',
    jsonb_build_object(
      'assignment_id', '__radar_assignment_invalid__',
      'assignment_workflow_id', 'assignment-test-workflow',
      'assignment_event', 'ASSIGNED',
      'assignment_state', 'ASSIGNED'
    )
  );

  if not exists (
    select 1 from radar.reconciliation_events
    where code = 'ASSIGNMENT_ENVELOPE_INVALID'
      and detail->>'message_id' = invalid_message
  ) then
    raise exception 'INVALID_ASSIGNMENT_OBSERVATION_MISSING';
  end if;

  select count(*) into event_count_before
  from radar.assignment_events
  where assignment_id = assignment_id_value;

  select count(*) into reconciliation_count_before
  from radar.reconciliation_events
  where detail->>'message_id' in (fork_message, pending_message, invalid_message)
    and code in ('ASSIGNMENT_EVENT_CONFLICT','ASSIGNMENT_EVENT_PENDING_PREDECESSOR','ASSIGNMENT_ENVELOPE_INVALID');

  perform radar.reconcile_bus_assignments_v1();

  if event_count_before <> (
    select count(*) from radar.assignment_events where assignment_id = assignment_id_value
  ) then
    raise exception 'ASSIGNMENT_EVENTS_NOT_IDEMPOTENT';
  end if;

  if reconciliation_count_before <> (
    select count(*) from radar.reconciliation_events
    where detail->>'message_id' in (fork_message, pending_message, invalid_message)
      and code in ('ASSIGNMENT_EVENT_CONFLICT','ASSIGNMENT_EVENT_PENDING_PREDECESSOR','ASSIGNMENT_ENVELOPE_INVALID')
  ) then
    raise exception 'ASSIGNMENT_RECONCILIATION_NOT_IDEMPOTENT';
  end if;
end
$$;

rollback;
