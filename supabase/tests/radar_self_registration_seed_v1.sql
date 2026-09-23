-- Qualification assertion for the current Radar recovery/self-registration seed.
-- First prove db reset already applied the configured seed. Only then replay the
-- same seed to prove idempotence without masking a broken db.seed integration.

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
  if (select count(*) from radar.nodes where identity_id = 'radar') <> 1
     or not exists (
       select 1
       from radar.nodes
       where node_id = stable_node
         and identity_id = 'radar'
         and runtime_kind = 'chatgpt_operator'
         and status = 'OFFLINE'
         and last_heartbeat is null
         and lease_expires_at is null
     ) then
    raise exception 'RADAR_SEED_PRE_REPLAY_STABLE_NODE_INVALID';
  end if;

  if (select count(*) from radar.endpoints where endpoint_id = 'radar-github-mailbox') <> 1
     or not exists (
       select 1
       from radar.endpoints
       where endpoint_id = 'radar-github-mailbox'
         and identity_id = 'radar'
         and node_id = stable_node
         and transport = 'github_branch'
         and address = 'bus/radar-v2'
         and status = 'ACTIVE'
     ) then
    raise exception 'RADAR_SEED_PRE_REPLAY_MAILBOX_INVALID';
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
  ) <> 6
  or exists (
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
    raise exception 'RADAR_SEED_PRE_REPLAY_SUBSCRIPTIONS_INVALID';
  end if;
end
$$;

rollback;

-- Replay only after the pre-replay assertions have proved db reset seeded state.
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
  if (select count(*) from radar.nodes where identity_id = 'radar') <> 1
     or not exists (
       select 1
       from radar.nodes
       where node_id = stable_node
         and identity_id = 'radar'
         and runtime_kind = 'chatgpt_operator'
         and status = 'OFFLINE'
         and last_heartbeat is null
         and lease_expires_at is null
     ) then
    raise exception 'RADAR_SEED_POST_REPLAY_STABLE_NODE_INVALID';
  end if;

  if (select count(*) from radar.endpoints where endpoint_id = 'radar-github-mailbox') <> 1
     or not exists (
       select 1
       from radar.endpoints
       where endpoint_id = 'radar-github-mailbox'
         and identity_id = 'radar'
         and node_id = stable_node
         and transport = 'github_branch'
         and address = 'bus/radar-v2'
         and status = 'ACTIVE'
     ) then
    raise exception 'RADAR_SEED_POST_REPLAY_MAILBOX_INVALID';
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
    raise exception 'RADAR_SEED_POST_REPLAY_SUBSCRIPTIONS_INVALID';
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
    raise exception 'RADAR_SEED_POST_REPLAY_UNEXPECTED_ACTIVE_SUBSCRIPTIONS';
  end if;
end
$$;

rollback;
