begin;

do $$
declare
  message_id_value text := '__radar_operator_view_message__';
  reply_id_value text := '__radar_operator_view_reply__';
  assignment_id_value text := '__radar_operator_view_assignment__';
  assignment_message_value text := '__radar_operator_view_assignment_root__';
begin
  insert into radar.identities(identity_id, display_name, lifecycle_status, metadata)
  values
    ('operator-view-sender', 'Operator View Sender', 'ACTIVE', '{}'::jsonb),
    ('operator-view-recipient', 'Operator View Recipient', 'ACTIVE', '{}'::jsonb)
  on conflict (identity_id) do nothing;

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    message_id_value, 1, '2026-09-03T00:30:00Z', 'operator-view-sender',
    array['operator-view-recipient'], 'chat_bus', 'bus_message', 3, true,
    array['github://operator-view/message'], repeat('6',64), 'operator-view:message',
    jsonb_build_object('subject','operator view evidence target')
  );

  if not exists (
    select 1 from radar.identity_message_status_v1
    where message_id = message_id_value
      and recipient_identity_id = 'operator-view-recipient'
      and delivery_outcome = 'INDEXED_NOT_DELIVERED'
      and reply_evidence_status = 'NO_EXPLICIT_REPLY_EVIDENCE'
  ) then
    raise exception 'MESSAGE_STATUS_WITHOUT_REPLY_EVIDENCE_MISSING';
  end if;

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    reply_id_value, 1, '2026-09-03T00:31:00Z', 'operator-view-recipient',
    array['operator-view-sender'], 'chat_bus', 'bus_message', 3, false,
    array['github://operator-view/reply'], repeat('7',64), 'operator-view:reply',
    jsonb_build_object('reply_to',message_id_value,'subject','operator view evidence reply')
  );

  if not exists (
    select 1 from radar.identity_message_status_v1
    where message_id = message_id_value
      and recipient_identity_id = 'operator-view-recipient'
      and reply_evidence_status = 'EXPLICIT_REPLY_EVIDENCE'
      and evidence_ref = 'github://operator-view/reply'
  ) then
    raise exception 'MESSAGE_STATUS_REPLY_EVIDENCE_MISSING';
  end if;

  insert into radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) values (
    assignment_message_value, 1, '2026-09-03T00:32:00Z', 'operator-view-sender',
    array['operator-view-recipient'], 'chat_bus', 'bus_message', 3, true,
    array['github://operator-view/assignment'], repeat('8',64), 'operator-view:assignment',
    jsonb_build_object(
      'assignment_id',assignment_id_value,
      'assignment_workflow_id','operator-view-workflow',
      'assignment_assignee','operator-view-recipient',
      'assignment_event','ASSIGNED',
      'assignment_state','ASSIGNED',
      'assignment_protected_authority','false'
    )
  );

  if not exists (
    select 1 from radar.open_assignments_v1
    where assignment_id = assignment_id_value
      and assignee_identity_id = 'operator-view-recipient'
      and current_state = 'assigned'
      and source_message_id = assignment_message_value
      and operation_id = assignment_message_value
      and receipt_sha256 = repeat('8',64)
  ) then
    raise exception 'OPEN_ASSIGNMENT_VIEW_MISSING';
  end if;
end
$$;

rollback;
