-- Run after applying 20260906133630_radar_node_routing_hardening_v1.sql.
-- Fixture writes are rolled back; assertions fail loudly.

begin;

insert into radar.identities(identity_id, display_name, aliases)
values
  ('radar-node-route-a', 'Radar Node Route A', '{}'),
  ('radar-node-route-b', 'Radar Node Route B', '{}');

insert into radar.nodes(
  node_id, identity_id, runtime_kind, status, last_heartbeat, lease_expires_at
)
values
  ('11111111-1111-4111-8111-111111111111', 'radar-node-route-a', 'test', 'ONLINE', now(), now() + interval '10 minutes'),
  ('22222222-2222-4222-8222-222222222222', 'radar-node-route-a', 'test', 'ONLINE', now(), now() - interval '1 second'),
  ('33333333-3333-4333-8333-333333333333', 'radar-node-route-a', 'test', 'ONLINE', null, now() + interval '10 minutes'),
  ('44444444-4444-4444-8444-444444444444', 'radar-node-route-a', 'test', 'ONLINE', now(), null),
  ('55555555-5555-4555-8555-555555555555', 'radar-node-route-a', 'test', 'PAUSED', now(), now() + interval '10 minutes');

-- A node-bound subscription is valid only when node ownership matches identity.
insert into radar.subscriptions(identity_id, node_id, domain, intent, min_priority, active)
values (
  'radar-node-route-a',
  '11111111-1111-4111-8111-111111111111',
  'database',
  'event',
  4,
  true
);

-- Once a node acquires subscriptions, later node-identity reassignment must not
-- silently transfer or invalidate that authority relationship.
do $$
begin
  begin
    update radar.nodes
    set identity_id = 'radar-node-route-b'
    where node_id = '11111111-1111-4111-8111-111111111111';
    raise exception 'RADAR_TEST_EXPECTED_NODE_IDENTITY_IMMUTABLE';
  exception
    when check_violation then
      if sqlerrm not like '%RADAR_NODE_IDENTITY_IMMUTABLE%' then
        raise;
      end if;
  end;
end
$$;

do $$
begin
  begin
    insert into radar.subscriptions(identity_id, node_id, domain, intent, min_priority, active)
    values (
      'radar-node-route-b',
      '11111111-1111-4111-8111-111111111111',
      'system',
      'event',
      4,
      true
    );
    raise exception 'RADAR_TEST_EXPECTED_NODE_IDENTITY_MISMATCH';
  exception
    when check_violation then
      if sqlerrm not like '%RADAR_SUBSCRIPTION_NODE_IDENTITY_MISMATCH%' then
        raise;
      end if;
  end;
end
$$;

do $$
begin
  begin
    insert into radar.subscriptions(identity_id, node_id, domain, intent, min_priority, active)
    values ('radar-node-route-a', null, 'system', 'event', 4, true);
    raise exception 'RADAR_TEST_EXPECTED_ACTIVE_NODE_REQUIRED';
  exception
    when check_violation then
      if sqlerrm not like '%RADAR_ACTIVE_SUBSCRIPTION_NODE_REQUIRED%'
         and sqlerrm not like '%radar_subscriptions_active_node_bound%' then
        raise;
      end if;
  end;
end
$$;

-- Expired, heartbeat-less, and lease-less routable statuses all fail closed.
select radar.mark_stale_nodes_offline(interval '5 minutes');

do $$
begin
  if (select status from radar.nodes where node_id = '11111111-1111-4111-8111-111111111111') <> 'ONLINE' then
    raise exception 'RADAR_LIVE_NODE_INCORRECTLY_OFFLINED';
  end if;

  if exists (
    select 1
    from radar.nodes
    where node_id in (
      '22222222-2222-4222-8222-222222222222',
      '33333333-3333-4333-8333-333333333333',
      '44444444-4444-4444-8444-444444444444'
    )
      and status <> 'OFFLINE'
  ) then
    raise exception 'RADAR_STALE_OR_LEASELESS_NODE_REMAINED_ROUTABLE';
  end if;

  if (select status from radar.nodes where node_id = '55555555-5555-4555-8555-555555555555') <> 'PAUSED' then
    raise exception 'RADAR_PAUSED_NODE_STATUS_MUTATED';
  end if;
end
$$;

-- Invalid stale windows are rejected rather than disabling the safety bound.
do $$
begin
  begin
    perform radar.mark_stale_nodes_offline(interval '0 seconds');
    raise exception 'RADAR_TEST_EXPECTED_INVALID_STALE_INTERVAL';
  exception
    when invalid_parameter_value then
      if sqlerrm not like '%RADAR_INVALID_STALE_INTERVAL%' then
        raise;
      end if;
  end;
end
$$;

-- Heartbeat renewal restores a bounded live lease without changing identity.
select radar.touch_node('22222222-2222-4222-8222-222222222222', 'ONLINE');

do $$
begin
  if not exists (
    select 1
    from radar.nodes
    where node_id = '22222222-2222-4222-8222-222222222222'
      and identity_id = 'radar-node-route-a'
      and status = 'ONLINE'
      and last_heartbeat is not null
      and lease_expires_at > now()
  ) then
    raise exception 'RADAR_TOUCH_NODE_DID_NOT_RENEW_LEASE';
  end if;
end
$$;

-- Client roles must not recover EXECUTE through PostgreSQL's default PUBLIC grant.
do $$
declare
  sig text;
begin
  foreach sig in array array[
    'radar.assignment_ready(text)',
    'radar.mark_stale_nodes_offline(interval)',
    'radar.touch_node(uuid,text)',
    'radar.validate_subscription_node_identity()',
    'radar.prevent_node_identity_reassignment()'
  ]
  loop
    if has_function_privilege('anon', sig, 'EXECUTE')
       or has_function_privilege('authenticated', sig, 'EXECUTE') then
      raise exception 'RADAR_NODE_ROUTING_FUNCTION_EXECUTE_EXPOSED:%', sig;
    end if;
  end loop;
end
$$;

rollback;
