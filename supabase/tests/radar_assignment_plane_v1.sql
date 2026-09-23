begin;

-- Test: radar assignment projection & reconciliation (v1)
-- - Creates identities + a variety of messages (root, ack, stale fork, missing-predecessor, invalid envelope)
-- - Verifies projection of assignment and events, checks reconciliation observations
-- - Calls reconcile function and asserts idempotence of events & reconciliation records
-- Note: test runs inside a transaction and rolls back at the end.

do $$
declare
  -- Primary test ids
  assignment_id_value text := '__radar_assignment_test__';
  root_message text := '__radar_assignment_root__';
  ack_message text := '__radar_assignment_ack__';
  fork_message text := '__radar_assignment_fork__';
  pending_message text := '__radar_assignment_pending__';
  invalid_message text := '__radar_assignment_invalid__';
  ordinary_message text := '__radar_assignment_ordinary__';

  -- timestamps: keep them parametrized so it's easy to change base time
  ts_base timestamptz := '2026-09-03T00:00:00Z'::timestamptz;
  root_ts timestamptz := ts_base + interval '1 minute';
  ack_ts timestamptz := ts_base + interval '2 minute';
  fork_ts timestamptz := ts_base + interval '3 minute';
  pending_ts timestamptz := ts_base + interval '4 minute';
  invalid_ts timestamptz := ts_base + interval '5 minute';

  root_event bigint;
  ack_event bigint;
  event_count_before integer;
  reconciliation_count_before integer;
begin
  -- Ensure test identities exist (idempotent)
  insert into radar.identities(identity_id, display_name, lifecycle_status, metadata)
  values
    ('assignment-test-coordinator', 'Assignment Test Coordinator', 'ACTIVE', '{}'::jsonb),
    ('assignment-test-worker', 'Assignment Test Worker', 'ACTIVE', '{}'::jsonb)
  on conflict (identity_id) do nothing;

  -- An ordinary message (should NOT create an assignment)
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    ordinary_message, 1, ts_base, 'assignment-test-coordinator',
    array['assignment-test-worker'], 'chat_bus', 'bus_message', 3, false,
    array['github://assignment-test/ordinary'], repeat('0', 64),
    'assignment-test:ordinary',
    jsonb_build_object('subject', 'ordinary message')
  )
  on conflict (message_id) do nothing;

  -- Assert that no assignment was created by the ordinary message
  if exists (select 1 from radar.assignments where assignment_id = assignment_id_value) then
    raise exception 'ORDINARY_MESSAGE_CREATED_ASSIGNMENT: assignment_id=%', assignment_id_value;
  end if;

  -- Insert explicit assignment "root" message (requires_ack => true)
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    root_message, 1, root_ts, 'assignment-test-coordinator',
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
      -- JSON boolean (not a string)
      'assignment_protected_authority', false
    )
  )
  on conflict (message_id) do nothing;

  -- Verify assignment projected correctly
  if not exists (
    select 1 from radar.assignments
    where assignment_id = assignment_id_value
      and workflow_id = 'assignment-test-workflow'
      and current_state = 'ASSIGNED'
      and assignee_identity_id = 'assignment-test-worker'
      and source_message_id = root_message
      and protected_authority = false
  ) then
    raise exception 'ASSIGNMENT_ROOT_NOT_PROJECTED: assignment_id=%', assignment_id_value;
  end if;

  -- Capture root event id
  select event_id into root_event
  from radar.assignment_events
  where assignment_id = assignment_id_value and operation_id = root_message
  limit 1;

  if root_event is null then
    raise exception 'ASSIGNMENT_ROOT_EVENT_MISSING: operation_id=%', root_message;
  end if;

  -- Insert acknowledgement message (worker ack)
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    ack_message, 1, ack_ts, 'assignment-test-worker',
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
      'assignment_protected_authority', false
    )
  )
  on conflict (message_id) do nothing;

  select event_id into ack_event
  from radar.assignment_events
  where assignment_id = assignment_id_value and operation_id = ack_message
  limit 1;

  if ack_event is null then
    raise exception 'ASSIGNMENT_ACK_EVENT_MISSING: operation_id=%', ack_message;
  end if;

  -- Verify the relationship between ack and root events and the receipt hash
  if not exists (
    select 1 from radar.assignment_events
    where event_id = ack_event
      and predecessor_event_id = root_event
      and from_state = 'ASSIGNED'
      and to_state = 'ACKNOWLEDGED'
      and actor = 'assignment-test-worker'
      and receipt_sha256 = repeat('2', 64)
  ) then
    raise exception 'ASSIGNMENT_ACK_EVENT_BAD_RECEIPT: ack_event=%', ack_event;
  end if;

  -- Verify assignment current state advanced
  if not exists (
    select 1 from radar.assignments
    where assignment_id = assignment_id_value
      and current_state = 'ACKNOWLEDGED'
      and current_event_id = ack_event
  ) then
    raise exception 'ASSIGNMENT_CURRENT_STATE_NOT_ADVANCED: assignment_id=%', assignment_id_value;
  end if;

  ---------------------------------------------------------------------------
  -- Stale fork: predecessor points to root (but name indicates it's a fork created after ACK)
  -- This MUST NOT advance the assignment since it's a stale fork.
  ---------------------------------------------------------------------------
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    fork_message, 1, fork_ts, 'assignment-test-worker',
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
      'assignment_protected_authority', false
    )
  )
  on conflict (message_id) do nothing;

  if exists (
    select 1 from radar.assignment_events
    where assignment_id = assignment_id_value and operation_id = fork_message
  ) then
    raise exception 'STALE_FORK_ADVANCED_ASSIGNMENT: fork_message=%', fork_message;
  end if;

  if not exists (
    select 1 from radar.reconciliation_events
    where code = 'ASSIGNMENT_EVENT_CONFLICT'
      and detail->>'message_id' = fork_message
      and detail->>'reason' = 'predecessor_is_not_current_assignment_event'
  ) then
    raise exception 'STALE_FORK_CONFLICT_OBSERVATION_MISSING: fork_message=%', fork_message;
  end if;

  ---------------------------------------------------------------------------
  -- Successor whose predecessor is not present -> should be observed as pending
  ---------------------------------------------------------------------------
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    pending_message, 1, pending_ts, 'assignment-test-worker',
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
      'assignment_protected_authority', false
    )
  )
  on conflict (message_id) do nothing;

  if not exists (
    select 1 from radar.reconciliation_events
    where code = 'ASSIGNMENT_EVENT_PENDING_PREDECESSOR'
      and detail->>'message_id' = pending_message
  ) then
    raise exception 'PENDING_PREDECESSOR_OBSERVATION_MISSING: pending_message=%', pending_message;
  end if;

  ---------------------------------------------------------------------------
  -- Explicit but incomplete assignment envelope -> should be observed as invalid
  ---------------------------------------------------------------------------
  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    invalid_message, 1, invalid_ts, 'assignment-test-coordinator',
    array['assignment-test-worker'], 'chat_bus', 'bus_message', 3, false,
    array['github://assignment-test/invalid'], repeat('5', 64),
    'assignment-test:invalid',
    jsonb_build_object(
      'assignment_id', '__radar_assignment_invalid__',
      'assignment_workflow_id', 'assignment-test-workflow',
      'assignment_event', 'ASSIGNED',
      'assignment_state', 'ASSIGNED'
      -- note: missing assignee -> invalid by design
    )
  )
  on conflict (message_id) do nothing;

  if not exists (
    select 1 from radar.reconciliation_events
    where code = 'ASSIGNMENT_ENVELOPE_INVALID'
      and detail->>'message_id' = invalid_message
  ) then
    raise exception 'INVALID_ASSIGNMENT_OBSERVATION_MISSING: invalid_message=%', invalid_message;
  end if;

  -- Record counts before reconciliation to check idempotence
  select count(*) into event_count_before
  from radar.assignment_events
  where assignment_id = assignment_id_value;

  select count(*) into reconciliation_count_before
  from radar.reconciliation_events
  where detail->>'message_id' in (fork_message, pending_message, invalid_message)
    and code in ('ASSIGNMENT_EVENT_CONFLICT','ASSIGNMENT_EVENT_PENDING_PREDECESSOR','ASSIGNMENT_ENVELOPE_INVALID');

  -- Run the reconciliation job (no-op if already reconciled)
  perform radar.reconcile_bus_assignments_v1();

  -- Ensure reconciliation is idempotent (no duplicate events or observations were created)
  if event_count_before <> (
    select count(*) from radar.assignment_events where assignment_id = assignment_id_value
  ) then
    raise exception 'ASSIGNMENT_EVENTS_NOT_IDEMPOTENT: assignment_id=%', assignment_id_value;
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
