-- Run after applying 20260902_radar_control_plane_v1.sql to a test/provider database.
-- Assertions fail loudly and fixture writes are rolled back.

begin;

do $$
begin
  if not exists (select 1 from pg_namespace where nspname = 'radar') then
    raise exception 'RADAR_SCHEMA_MISSING';
  end if;
  if has_schema_privilege('anon', 'radar', 'USAGE') then
    raise exception 'RADAR_ANON_SCHEMA_USAGE';
  end if;
  if has_schema_privilege('authenticated', 'radar', 'USAGE') then
    raise exception 'RADAR_AUTH_SCHEMA_USAGE';
  end if;
end
$$;

do $$
declare
  required text[] := array[
    'identities','nodes','endpoints','subscriptions','messages','delivery_events',
    'acknowledgements','dead_letters','assignments','assignment_events','dependencies',
    'health_events','reconciliation_events','telemetry'
  ];
  name text;
begin
  foreach name in array required loop
    if to_regclass('radar.' || name) is null then
      raise exception 'RADAR_TABLE_MISSING:%', name;
    end if;
    if has_table_privilege('anon', 'radar.' || name, 'SELECT')
       or has_table_privilege('authenticated', 'radar.' || name, 'SELECT')
       or has_table_privilege('anon', 'radar.' || name, 'INSERT')
       or has_table_privilege('authenticated', 'radar.' || name, 'INSERT') then
      raise exception 'RADAR_CLIENT_PRIVILEGE_EXPOSED:%', name;
    end if;
  end loop;
end
$$;

insert into radar.identities(identity_id, display_name, aliases)
values ('radar-test-a', 'Radar Test A', '{}'), ('radar-test-b', 'Radar Test B', '{}');

insert into radar.nodes(identity_id, runtime_kind, status, last_heartbeat)
values ('radar-test-a', 'test', 'ONLINE', now() - interval '10 minutes');

select radar.mark_stale_nodes_offline(interval '5 minutes');

do $$
begin
  if not exists (
    select 1 from radar.nodes
    where identity_id = 'radar-test-a' and status = 'OFFLINE'
  ) then
    raise exception 'RADAR_STALE_NODE_NOT_OFFLINE';
  end if;
  if not exists (
    select 1 from radar.identities where identity_id = 'radar-test-a'
  ) then
    raise exception 'RADAR_IDENTITY_LOST_WITH_NODE';
  end if;
end
$$;

insert into radar.assignments(assignment_id, workflow_id, current_state)
values
  ('radar-pred', 'test', 'RUNNING'),
  ('radar-succ', 'test', 'ASSIGNED');
insert into radar.dependencies(predecessor_assignment_id, successor_assignment_id)
values ('radar-pred', 'radar-succ');

do $$
begin
  if radar.assignment_ready('radar-succ') then
    raise exception 'RADAR_DEPENDENCY_FALSE_READY';
  end if;
end
$$;

update radar.assignments set current_state = 'CONFIRMED' where assignment_id = 'radar-pred';

do $$
begin
  if not radar.assignment_ready('radar-succ') then
    raise exception 'RADAR_DEPENDENCY_NOT_READY';
  end if;
end
$$;

insert into radar.dead_letters(message_id, failure_stage, failure_code, envelope, diagnostic)
values ('radar-test-message', 'routing', 'NO_ROUTE', '{"message_id":"radar-test-message"}'::jsonb, 'test');

do $$
begin
  if not exists (
    select 1 from radar.dead_letters
    where message_id = 'radar-test-message'
      and replay_state = 'PENDING'
      and applicability = 'UNKNOWN'
  ) then
    raise exception 'RADAR_DLQ_NOT_DURABLE';
  end if;
end
$$;

rollback;
