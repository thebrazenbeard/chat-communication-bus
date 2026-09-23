-- Contract checks for Radar visual identity V1.
-- Git remains canonical; provider state stores metadata only, never image bytes.

do $$
declare
  t regclass;
  rls_enabled boolean;
  binary_columns_count int;
  pk_on_asset_id boolean;
  fk_references_identities boolean;
  offending_binary_cols text;
  missing_required_cols text;
begin
  -- Ensure schema exists.
  if not exists (select 1 from pg_namespace where nspname = 'radar') then
    raise exception 'RADAR_SCHEMA_MISSING';
  end if;

  -- Ensure table exists.
  begin
    t := 'radar.identity_visuals'::regclass;
  exception when undefined_table then
    raise exception 'RADAR_IDENTITY_VISUALS_TABLE_MISSING';
  end;

  -- RLS must be enabled. The V1 migration intentionally defines no client
  -- policy: anon/authenticated have no table privileges, while service_role is
  -- the explicit metadata projection role.
  select c.relrowsecurity into rls_enabled from pg_class c where c.oid = t;
  if not coalesce(rls_enabled, false) then
    raise exception 'RADAR_IDENTITY_VISUALS_RLS_DISABLED';
  end if;

  if has_table_privilege('anon', 'radar.identity_visuals', 'SELECT')
     or has_table_privilege('anon', 'radar.identity_visuals', 'INSERT')
     or has_table_privilege('anon', 'radar.identity_visuals', 'UPDATE')
     or has_table_privilege('anon', 'radar.identity_visuals', 'DELETE')
     or has_table_privilege('authenticated', 'radar.identity_visuals', 'SELECT')
     or has_table_privilege('authenticated', 'radar.identity_visuals', 'INSERT')
     or has_table_privilege('authenticated', 'radar.identity_visuals', 'UPDATE')
     or has_table_privilege('authenticated', 'radar.identity_visuals', 'DELETE') then
    raise exception 'RADAR_IDENTITY_VISUALS_CLIENT_PRIVILEGE_EXPOSED';
  end if;

  if not has_table_privilege('service_role', 'radar.identity_visuals', 'SELECT')
     or not has_table_privilege('service_role', 'radar.identity_visuals', 'INSERT')
     or not has_table_privilege('service_role', 'radar.identity_visuals', 'UPDATE')
     or not has_table_privilege('service_role', 'radar.identity_visuals', 'DELETE') then
    raise exception 'RADAR_IDENTITY_VISUALS_SERVICE_PRIVILEGE_MISSING';
  end if;

  -- Forbid storing binary payloads in-table.
  select count(*) into binary_columns_count
  from information_schema.columns
  where table_schema = 'radar'
    and table_name = 'identity_visuals'
    and (udt_name = 'bytea' or data_type = 'bytea' or column_name in ('image_bytes', 'blob', 'body'));

  if binary_columns_count <> 0 then
    select string_agg(column_name, ', ') into offending_binary_cols
    from information_schema.columns
    where table_schema = 'radar'
      and table_name = 'identity_visuals'
      and (udt_name = 'bytea' or data_type = 'bytea' or column_name in ('image_bytes', 'blob', 'body'));

    raise exception 'RADAR_IDENTITY_VISUALS_BINARY_STORAGE_FORBIDDEN: %', offending_binary_cols;
  end if;

  -- The V1 schema keys visual metadata by asset_id.
  select exists (
    select 1
    from information_schema.table_constraints tc
    join information_schema.key_column_usage kcu
      on tc.constraint_name = kcu.constraint_name
     and tc.constraint_schema = kcu.constraint_schema
    where tc.table_schema = 'radar'
      and tc.table_name = 'identity_visuals'
      and tc.constraint_type = 'PRIMARY KEY'
      and kcu.column_name = 'asset_id'
  ) into pk_on_asset_id;

  if not pk_on_asset_id then
    raise exception 'RADAR_IDENTITY_VISUALS_PK_MISSING_OR_NOT_ON_ASSET_ID';
  end if;

  if to_regclass('radar.identities') is null then
    raise exception 'RADAR_IDENTITIES_TABLE_MISSING';
  end if;

  -- Ensure identity_id is backed by a foreign key to radar.identities.
  select exists (
    select 1
    from pg_constraint c
    where c.conrelid = t
      and c.contype = 'f'
      and c.confrelid = ('radar.identities'::regclass)
  ) into fk_references_identities;

  if not fk_references_identities then
    if exists (
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
      raise exception 'RADAR_IDENTITY_VISUALS_IDENTITY_FK_REFERENCES_WRONG_TABLE';
    else
      raise exception 'RADAR_IDENTITY_VISUALS_IDENTITY_FK_MISSING';
    end if;
  end if;

  select string_agg(colname, ', ') into missing_required_cols from (
    values ('asset_id'), ('identity_id'), ('created_at'), ('updated_at')
  ) as required(colname)
  where not exists (
    select 1 from information_schema.columns c
    where c.table_schema = 'radar'
      and c.table_name = 'identity_visuals'
      and c.column_name = required.colname
  );

  if missing_required_cols is not null then
    raise exception 'RADAR_IDENTITY_VISUALS_MISSING_COLUMNS: %', missing_required_cols;
  end if;
end
$$;
