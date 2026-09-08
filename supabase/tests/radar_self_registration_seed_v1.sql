-- Qualification assertion for the current Radar recovery/self-registration seed.
-- db reset must have already applied the full migration chain and configured seed.
-- Replay the seed once more here to prove idempotence before checking exact state.

\ir ../seed/radar_v1.sql

begin;

do $$
declare
  stable_node constant uuid := '72616461-722d-4000-8000-000000000001'::uuid;
  expected_domains constant text[] := array[
    'coordination',
    'system',
    'security',
    'database',
    'repository',
    'protocol'
  ];
begin
  if (select count(*) from radar.nodes where identity_id = 'radar') <> 1 then
    raise exception 'RADAR_SEED_EXPECTED_EXACTLY_ONE_RADAR_NODE';
  end if;

  if not exists (
    select 1
    from radar.nodes
    where node_id = stable_node
      and identity_id = 'radar'
      and runtime_kind = 'chatgpt_operator'
      and status = 'OFFLINE'
      and last_heartbeat is null
      and lease_expires_at is null
  ) then
    raise exception 'RADAR_SEED_STABLE_NODE_STATE_INCORRECT';
  end if;

  if (select count(*) from radar.endpoints where endpoint_id = 'radar-github-mailbox') <> 1 then
    raise exception 'RADAR_SEED_EXPECTED_EXACTLY_ONE_MAILBOX_ENDPOINT';
  end if;

  if not exists (
    select 1
    from radar.endpoints
    where endpoint_id = 'radar-github-mailbox'
      and identity_id = 'radar'
      and node_id = stable_node
      and transport = 'github_branch'
      and address = 'bus/radar-v2'
      and status = 'ACTIVE'
  ) then
    raise exception 'RADAR_SEED_MAILBOX_BINDING_INCORRECT';
  end if;

  if exists (
    select 1
    from radar.subscriptions
    where identity_id = 'radar'
      and active
      and node_id is null
  ) then
    raise exception 'RADAR_SEED_ACTIVE_IDENTITY_ONLY_SUBSCRIPTION_REMAINED';
  end if;

  if (
    select count(*)
    from radar.subscriptions
    where identity_id = 'radar'
      and node_id = stable_node
      and domain = any(expected_domains)
      and intent is null
      and min_priority = 4
      and active
  ) <> 6 then
    raise exception 'RADAR_SEED_EXPECTED_SIX_ACTIVE_NODE_BOUND_SUBSCRIPTIONS';
  end if;

  if exists (
    select 1
    from radar.subscriptions
    where identity_id = 'radar'
      and active
      and (
        node_id is distinct from stable_node
        or domain <> all(expected_domains)
        or intent is not null
        or min_priority <> 4
      )
  ) then
    raise exception 'RADAR_SEED_UNEXPECTED_ACTIVE_RADAR_SUBSCRIPTION';
  end if;
end
$$;

rollback;
