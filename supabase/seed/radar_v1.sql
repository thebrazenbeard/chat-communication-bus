-- Idempotent Radar V1 self-registration / topology seed.
-- This is provider projection, not the canonical identity contract.

begin;

insert into radar.identities(identity_id, display_name, aliases, lifecycle_status, metadata)
values (
  'radar',
  'Radar',
  '{}',
  'ACTIVE',
  jsonb_build_object(
    'identity_kind', 'repository_owner_operator',
    'repository', 'thebrazenbeard/chat-communication-bus',
    'patrick_override', true,
    'canonical_state', 'github',
    'integration_branch', 'radar/control-plane-v1',
    'mailbox_branch', 'bus/radar-v1',
    'contract_ref', 'architecture/contracts/RADAR_SELF_REGISTRATION_V1.json'
  )
)
on conflict (identity_id) do update
set display_name = excluded.display_name,
    aliases = excluded.aliases,
    lifecycle_status = excluded.lifecycle_status,
    metadata = excluded.metadata,
    updated_at = now();

insert into radar.endpoints(endpoint_id, identity_id, transport, address, status, metadata)
values
  (
    'radar-github-repository',
    'radar',
    'github',
    'thebrazenbeard/chat-communication-bus',
    'ACTIVE',
    jsonb_build_object('role', 'canonical_durable_home')
  ),
  (
    'radar-github-mailbox',
    'radar',
    'github_branch',
    'bus/radar-v1',
    'ACTIVE',
    jsonb_build_object('role', 'sole_writer_mailbox')
  ),
  (
    'radar-chatgpt-operator',
    'radar',
    'chatgpt',
    'operator-interface',
    'ACTIVE',
    jsonb_build_object(
      'session_is_identity', false,
      'role', 'interactive_operator_surface'
    )
  )
on conflict (endpoint_id) do update
set identity_id = excluded.identity_id,
    transport = excluded.transport,
    address = excluded.address,
    status = excluded.status,
    metadata = excluded.metadata,
    updated_at = now();

insert into radar.subscriptions(identity_id, domain, intent, min_priority, active)
values
  ('radar', 'coordination', null, 4, true),
  ('radar', 'system', null, 4, true),
  ('radar', 'security', null, 4, true),
  ('radar', 'database', null, 4, true),
  ('radar', 'repository', null, 4, true),
  ('radar', 'protocol', null, 4, true)
on conflict (identity_id, domain, coalesce(intent, ''), min_priority)
do nothing;

commit;
