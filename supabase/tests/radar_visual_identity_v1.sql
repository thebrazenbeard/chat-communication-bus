-- Contract checks for Radar visual identity V1.
-- Improved: schema/table existence handling, RLS+policies checks, clearer error messages,
-- explicit check that FK references radar.identities, and listing offending columns where relevant.

do $$
declare
  t regclass;
  rls_enabled boolean;
  binary_columns_count int;
  pk_on_id boolean;
  fk_references_identities boolean;
  policies_count int;
  offending_binary_cols text;
  missing_required_cols text;
begin
  -- Ensure schema exists
  if not exists (select 1 from pg_namespace where nspname = 'radar') then
    raise exception 'RADAR_SCHEMA_MISSING';
  end if;

  -- Ensure table exists (using regclass so undefined_table is caught)
  begin
    t := 'radar.identity_visuals'::regclass;
  exception when undefined_table then
    raise exception 'RADAR_IDENTITY_VISUALS_TABLE_MISSING';
  end;

  -- RLS must be enabled
  select c.relrowsecurity into rls_enabled from pg_class c where c.oid = t;
  if not coalesce(rls_enabled, false) then
    raise exception 'RADAR_IDENTITY_VISUALS_RLS_DISABLED';
  end if;

  -- Require at least one RLS policy (helps avoid accidentally locking the table with RLS on but no policies)
  select count(*) into policies_count from pg_policy p where p.polrelid = t;
  if policies_count = 0 then
    raise exception 'RADAR_IDENTITY_VISUALS_RLS_NO_POLICIES';
  end if;

  -- Forbid storing binary payloads in-table (explicitly report offending columns)
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

  -- Ensure there is a primary key and that it includes column "id"
  select exists (
    select 1
    from information_schema.table_constraints tc
    join information_schema.key_column_usage kcu
      on tc.constraint_name = kcu.constraint_name
     and tc.constraint_schema = kcu.constraint_schema
    where tc.table_schema = 'radar'
      and tc.table_name = 'identity_visuals'
      and tc.constraint_type = 'PRIMARY KEY'
      and kcu.column_name = 'id'
  ) into pk_on_id;

  if not pk_on_id then
    raise exception 'RADAR_IDENTITY_VISUALS_PK_MISSING_OR_NOT_ON_ID';
  end if;

  -- Ensure radar.identities exists (so we can assert FK references it)
  if to_regclass('radar.identities') is null then
    raise exception 'RADAR_IDENTITIES_TABLE_MISSING';
  end if;

  -- Ensure a foreign key exists that references radar.identities
  select exists (
    select 1
    from pg_constraint c
    where c.conrelid = t
      and c.contype = 'f'
      and c.confrelid = ('radar.identities'::regclass)
  ) into fk_references_identities;

  if not fk_references_identities then
    -- Distinguish between "no FK at all" and "FK exists but references wrong table"
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

  -- Check presence of commonly-required columns (adjust list/types to your schema expectations)
  select string_agg(colname, ', ') into missing_required_cols from (
    values ('id'), ('identity_id'), ('created_at'), ('updated_at')
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
