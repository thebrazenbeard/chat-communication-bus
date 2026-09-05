-- Run after applying 20260902_radar_control_plane_v1.sql to a test/provider database.
-- Assertions fail loudly and fixture writes are rolled back.
-- Improvements:
--  - Expanded privilege checks (SELECT/INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES)
--  - Ensure no EXECUTE privilege on schema functions for client roles
--  - Ensure no sequence privileges exposed to client roles
--  - Use PERFORM for side-effect-only function calls
--  - Clearer comments and diagnostic exception names

begin;

-- Basic schema & schema-usage checks
do $$
begin
  if not exists (select 1 from pg_namespace where nspname = 'radar') then
    raise exception 'RADAR_SCHEMA_MISSING';
  end if;

  -- Ensure neither anon nor authenticated have USAGE on the radar schema
  if has_schema_privilege('anon', 'radar', 'USAGE') then
    raise exception 'RADAR_ANON_SCHEMA_USAGE';
  end if;
  if has_schema_privilege('authenticated', 'radar', 'USAGE') then
    raise exception 'RADAR_AUTH_SCHEMA_USAGE';
  end if;
end
$$;

-- Tables exist and are not directly accessible by client roles
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

    -- Disallow typical client privileges on tables: SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES
    if has_table_privilege('anon', 'radar.' || name, 'SELECT')
       or has_table_privilege('authenticated', 'radar.' || name, 'SELECT')
       or has_table_privilege('anon', 'radar.' || name, 'INSERT')
       or has_table_privilege('authenticated', 'radar.' || name, 'INSERT')
       or has_table_privilege('anon', 'radar.' || name, 'UPDATE')
       or has_table_privilege('authenticated', 'radar.' || name, 'UPDATE')
       or has_table_privilege('anon', 'radar.' || name, 'DELETE')
       or has_table_privilege('authenticated', 'radar.' || name, 'DELETE')
       or has_table_privilege('anon', 'radar.' || name, 'TRUNCATE')
       or has_table_privilege('authenticated', 'radar.' || name, 'TRUNCATE')
       or has_table_privilege('anon', 'radar.' || name, 'REFERENCES')
       or has_table_privilege('authenticated', 'radar.' || name, 'REFERENCES')
    then
      raise exception 'RADAR_CLIENT_PRIVILEGE_EXPOSED:%', name;
    end if;
  end loop;
end
$$;

-- Functions in the radar schema should not be executable by client roles
do $$
declare
  fn record;
  sig text;
begin
  for fn in
    select p.oid, n.nspname as schema_name, p.proname,
           pg_get_function_identity_arguments(p.oid) as args
    from pg_proc p
    join pg_namespace n on p.pronamespace = n.oid
    where n.nspname = 'radar'
  loop
    sig := format('radar.%s(%s)', fn.proname, fn.args);
    -- has_function_privilege accepts a function signature; test anon/authenticated
    if has_function_privilege('anon', sig, 'EXECUTE')
       or has_function_privilege('authenticated', sig, 'EXECUTE') then
      raise exception 'RADAR_FUNCTION_EXECUTE_EXPOSED:%', sig;
    end if;
  end loop;
end
$$;

-- Ensure sequences (if any) are not usable by client roles (USAGE/SELECT)
do $$
declare
  seq record;
begin
  for seq in
    select quote_ident(n.nspname) || '.' || quote_ident(c.relname) as seqname
    from pg_class c
    join pg_namespace n on c.relnamespace = n.oid
    where c.relkind = 'S' and n.nspname = 'radar'
  loop
    if has_sequence_privilege('anon', seq.seqname, 'USAGE')
       or has_sequence_privilege('authenticated', seq.seqname, 'USAGE')
       or has_sequence_privilege('anon', seq.seqname, 'SELECT')
       or has_sequence_privilege('authenticated', seq.seqname, 'SELECT') then
      raise exception 'RADAR_SEQUENCE_PRIVILEGE_EXPOSED:%', seq.seqname;
    end if;
  end loop;
end
$$;

-- Fixtures (rolled back at end)
insert into radar.identities(identity_id, display_name, aliases)
values ('radar-test-a', 'Radar Test A', '{}'), ('radar-test-b', 'Radar Test B', '{}');

insert into radar.nodes(identity_id, runtime_kind, status, last_heartbeat)
values ('radar-test-a', 'test', 'ONLINE', now() - interval '10 minutes');

-- Use PERFORM for side-effect only call
perform radar.mark_stale_nodes_offline(interval '5 minutes');

-- Verify the node was marked offline and identity row remains
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

-- Dependency/assignment behaviour: ensure dependency prevents readiness, then changes state to allow readiness
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

-- Dead letter queue expectations
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
