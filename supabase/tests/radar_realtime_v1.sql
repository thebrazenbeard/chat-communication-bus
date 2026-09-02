-- Contract for Radar V1 selective Postgres Changes publication.
-- High-volume message payload rows are intentionally excluded.

do $$
declare
  required text[] := array['nodes','assignments','dependencies','acknowledgements','reconciliation_events'];
  forbidden text[] := array['messages','telemetry','delivery_events'];
  name text;
begin
  foreach name in array required loop
    if not exists (
      select 1 from pg_publication_tables
      where pubname = 'supabase_realtime'
        and schemaname = 'radar'
        and tablename = name
    ) then
      raise exception 'RADAR_REALTIME_TABLE_MISSING:%', name;
    end if;
  end loop;

  foreach name in array forbidden loop
    if exists (
      select 1 from pg_publication_tables
      where pubname = 'supabase_realtime'
        and schemaname = 'radar'
        and tablename = name
    ) then
      raise exception 'RADAR_REALTIME_HIGH_VOLUME_TABLE_EXPOSED:%', name;
    end if;
  end loop;
end
$$;
