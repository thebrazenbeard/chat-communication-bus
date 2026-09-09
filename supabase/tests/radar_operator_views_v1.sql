-- Test: radar operator views v1
-- Purpose: insert a message, a reply, and an assignment message then assert that
-- the radar read-only views expose the expected rows (reply evidence and open assignment).
-- Safe to run inside a transaction; this script uses ROLLBACK at the end so it doesn't persist test data.

BEGIN;

DO $$
/*
 Improvements made:
  - constants for test IDs use *_value names so they never collide with SQL columns
  - explicit LANGUAGE plpgsql on DO block (at bottom)
  - idempotent inserts (ON CONFLICT DO NOTHING)
  - explicit existence checks after inserts and clearer exception messages
  - comments to explain assertions
*/
DECLARE
  message_id_value CONSTANT text := 'operator-view-9001';
  reply_id_value CONSTANT text := 'operator-view-9002';
  assignment_id_value CONSTANT text := '__radar_operator_view_assignment__';
  assignment_message_value CONSTANT text := 'operator-view-9003';
BEGIN
  -- Ensure the identities exist (idempotent).
  INSERT INTO radar.identities(identity_id, display_name, lifecycle_status, metadata)
  VALUES
    ('operator-view-sender', 'Operator View Sender', 'ACTIVE', '{}'::jsonb),
    ('operator-view-recipient', 'Operator View Recipient', 'ACTIVE', '{}'::jsonb)
  ON CONFLICT (identity_id) DO NOTHING;

  -- Insert the original message (idempotent). If it already exists, that's fine.
  INSERT INTO radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) VALUES (
    message_id_value, 1, '2026-09-03T00:30:00Z', 'operator-view-sender',
    array['operator-view-recipient'], 'chat_bus', 'bus_message', 3, true,
    array['github://operator-view/message'], repeat('6',64), 'operator-view:message',
    jsonb_build_object('subject','operator view evidence target')
  )
  ON CONFLICT (message_id) DO NOTHING;

  -- Guard: ensure message inserted or already present.
  IF NOT EXISTS (SELECT 1 FROM radar.messages m WHERE m.message_id = message_id_value) THEN
    RAISE EXCEPTION 'INSERT_FAILED: message % not present in radar.messages', message_id_value;
  END IF;

  -- Assert: the read view should show an indexed but not delivered status with no reply evidence yet.
  IF NOT EXISTS (
    SELECT 1 FROM radar.identity_message_status_v1 ims
    WHERE ims.message_id = message_id_value
      AND ims.recipient_identity_id = 'operator-view-recipient'
      AND ims.delivery_outcome = 'INDEXED_NOT_DELIVERED'
      AND ims.reply_evidence_status = 'NO_EXPLICIT_REPLY_EVIDENCE'
  ) THEN
    RAISE EXCEPTION 'MESSAGE_STATUS_WITHOUT_REPLY_EVIDENCE_MISSING for message=%', message_id_value;
  END IF;

  -- Insert the reply message (idempotent).
  INSERT INTO radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) VALUES (
    reply_id_value, 1, '2026-09-03T00:31:00Z', 'operator-view-recipient',
    array['operator-view-sender'], 'chat_bus', 'bus_message', 3, false,
    array['github://operator-view/reply'], repeat('7',64), 'operator-view:reply',
    jsonb_build_object('reply_to',message_id_value,'subject','operator view evidence reply')
  )
  ON CONFLICT (message_id) DO NOTHING;

  IF NOT EXISTS (SELECT 1 FROM radar.messages m WHERE m.message_id = reply_id_value) THEN
    RAISE EXCEPTION 'INSERT_FAILED: reply message % not present in radar.messages', reply_id_value;
  END IF;

  -- After the reply, the identity_message_status_v1 view should reflect explicit reply evidence.
  IF NOT EXISTS (
    SELECT 1 FROM radar.identity_message_status_v1 ims
    WHERE ims.message_id = message_id_value
      AND ims.recipient_identity_id = 'operator-view-recipient'
      AND ims.reply_evidence_status = 'EXPLICIT_REPLY_EVIDENCE'
      AND ims.evidence_ref = 'github://operator-view/reply'
  ) THEN
    RAISE EXCEPTION 'MESSAGE_STATUS_REPLY_EVIDENCE_MISSING for message=% (expected evidence_ref=% )',
      message_id_value, 'github://operator-view/reply';
  END IF;

  -- Insert the assignment message (idempotent).
  INSERT INTO radar.messages(
    message_id, schema_version, created_at, sender, audience, domain, intent,
    priority, requires_ack, source_refs, content_hash, idempotency_key, payload
  ) VALUES (
    assignment_message_value, 1, '2026-09-03T00:32:00Z', 'operator-view-sender',
    array['operator-view-recipient'], 'chat_bus', 'bus_message', 3, true,
    array['github://operator-view/assignment'], repeat('8',64), 'operator-view:assignment',
    jsonb_build_object(
      'assignment_id',assignment_id_value,
      'assignment_workflow_id','operator-view-workflow',
      'assignment_assignee','operator-view-recipient',
      'assignment_event','ASSIGNED',
      'assignment_state','ASSIGNED',
      'assignment_protected_authority',false
    )
  )
  ON CONFLICT (message_id) DO NOTHING;

  IF NOT EXISTS (SELECT 1 FROM radar.messages m WHERE m.message_id = assignment_message_value) THEN
    RAISE EXCEPTION 'INSERT_FAILED: assignment message % not present in radar.messages', assignment_message_value;
  END IF;

  -- The open_assignments_v1 view should show the expected open assignment row.
  IF NOT EXISTS (
    SELECT 1 FROM radar.open_assignments_v1 oa
    WHERE oa.assignment_id = assignment_id_value
      AND oa.assignee_identity_id = 'operator-view-recipient'
      AND oa.current_state = 'assigned'
      AND oa.source_message_id = assignment_message_value
      AND oa.operation_id = assignment_message_value
      AND oa.receipt_sha256 = repeat('8',64)
  ) THEN
    RAISE EXCEPTION 'OPEN_ASSIGNMENT_VIEW_MISSING for assignment_id=% source_message=%',
      assignment_id_value, assignment_message_value;
  END IF;
END
$$ LANGUAGE plpgsql;

ROLLBACK;
