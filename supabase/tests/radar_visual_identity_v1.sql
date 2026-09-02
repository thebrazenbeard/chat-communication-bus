-- Contract checks for Radar visual identity V1.

do $$
declare
  rls_enabled boolean;
  binary_columns integer;
begin
  if to_regclass('radar.identity_visuals') is null then
    raise exception 'RADAR_IDENTITY_VISUALS_TABLE_MISSING';
  end if;

  select c.relrowsecurity
    into rls_enabled
  from pg_class c
  join pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'radar'
    and c.relname = 'identity_visuals';

  if not coalesce(rls_enabled, false) then
    raise exception 'RADAR_IDENTITY_VISUALS_RLS_DISABLED';
  end if;

  select count(*)
    into binary_columns
  from information_schema.columns
  where table_schema = 'radar'
    and table_name = 'identity_visuals'
    and (data_type = 'bytea' or column_name in ('image_bytes', 'blob', 'body'));

  if binary_columns <> 0 then
    raise exception 'RADAR_IDENTITY_VISUALS_BINARY_STORAGE_FORBIDDEN';
  end if;

  if not exists (
    select 1
    from information_schema.table_constraints tc
    join information_schema.key_column_usage kcu
      on tc.constraint_name = kcu.constraint_name
     and tc.constraint_schema = kcu.constraint_schema
    where tc.table_schema = 'radar'
      and tc.table_name = 'identity_visuals'
      and tc.constraint_type = 'FOREIGN KEY'
      and kcu.column_name = 'identity_id'
  ) then
    raise exception 'RADAR_IDENTITY_VISUALS_IDENTITY_FK_MISSING';
  end if;
end
$$;
