-- Idempotent CURRENT Radar self-registration / topology projection seed.
-- Apply only after the full current Git-held Radar migration chain.
-- GitHub remains canonical. This seed never proves liveness and never mints a lease.

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
    'mailbox_branch', 'bus/radar-v2',
    'historical_integration_branch', 'radar/control-plane-v1',
    'contract_ref', 'architecture/contracts/RADAR_SELF_REGISTRATION_V1.json'
  )
)
on conflict (identity_id) do update
set display_name = excluded.display_name,
    aliases = excluded.aliases,
    lifecycle_status = excluded.lifecycle_status,
    metadata = excluded.metadata,
    updated_at = now();

-- Stable recovery node. OFFLINE + NULL heartbeat/lease is intentional: seed state
-- is registration evidence, never runtime liveness/routing authority.
insert into radar.nodes(
  node_id, identity_id, runtime_kind, status, capabilities, last_heartbeat, metadata
)
values (
  '72616461-722d-4000-8000-000000000001'::uuid,
  'radar',
  'chatgpt_operator',
  'OFFLINE',
  array['github','routing','registry','workflow','dependency_tracking','reconciliation','telemetry','maintenance','supabase_projection'],
  null,
  jsonb_build_object(
    'role', 'recoverable_operator_node',
    'session_is_identity', false,
    'seeded_liveness', false
  )
)
on conflict (node_id) do update
set runtime_kind = excluded.runtime_kind,
    status = 'OFFLINE',
    capabilities = excluded.capabilities,
    last_heartbeat = null,
    lease_expires_at = null,
    metadata = excluded.metadata,
    updated_at = now();

insert into radar.endpoints(endpoint_id, identity_id, node_id, transport, address, status, metadata)
values
  (
    'radar-github-repository',
    'radar',
    null,
    'github',
    'thebrazenbeard/chat-communication-bus',
    'ACTIVE',
    jsonb_build_object('role', 'canonical_durable_home')
  ),
  (
    'radar-github-mailbox',
    'radar',
    '72616461-722d-4000-8000-000000000001'::uuid,
    'github_branch',
    'bus/radar-v2',
    'ACTIVE',
    jsonb_build_object('role', 'sole_writer_mailbox')
  ),
  (
    'radar-chatgpt-operator',
    'radar',
    '72616461-722d-4000-8000-000000000001'::uuid,
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
    node_id = excluded.node_id,
    transport = excluded.transport,
    address = excluded.address,
    status = excluded.status,
    metadata = excluded.metadata,
    updated_at = now();

insert into radar.subscriptions(identity_id, node_id, domain, intent, min_priority, active)
values
  ('radar', '72616461-722d-4000-8000-000000000001'::uuid, 'coordination', null, 4, true),
  ('radar', '72616461-722d-4000-8000-000000000001'::uuid, 'system', null, 4, true),
  ('radar', '72616461-722d-4000-8000-000000000001'::uuid, 'security', null, 4, true),
  ('radar', '72616461-722d-4000-8000-000000000001'::uuid, 'database', null, 4, true),
  ('radar', '72616461-722d-4000-8000-000000000001'::uuid, 'repository', null, 4, true),
  ('radar', '72616461-722d-4000-8000-000000000001'::uuid, 'protocol', null, 4, true)
on conflict do nothing;

update radar.subscriptions
set active = true
where identity_id = 'radar'
  and node_id = '72616461-722d-4000-8000-000000000001'::uuid
  and domain in ('coordination','system','security','database','repository','protocol')
  and intent is null
  and min_priority = 4;

commit;
