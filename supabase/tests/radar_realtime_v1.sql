-- Contract for Radar V1 Postgres Changes publication.
-- This assertion describes the intentionally published Radar tables in the
-- current provider contract. Publication membership is separate from table/RLS
-- privileges and does not by itself grant client access.

DO $$
DECLARE
  publication_name text := 'supabase_realtime';
  schema_name text := 'radar';
  required text[] := ARRAY[
    'acknowledgements',
    'assignments',
    'dependencies',
    'identity_visuals',
    'messages',
    'nodes',
    'reconciliation_events'
  ];
  published_tables text[];
  missing text[];
  unexpected text[];
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_publication AS p
    WHERE p.pubname = publication_name
  ) THEN
    RAISE EXCEPTION 'RADAR_REALTIME_PUBLICATION_MISSING: publication "%" does not exist', publication_name USING ERRCODE = 'P0001';
  END IF;

  SELECT array_agg(ppt.tablename ORDER BY ppt.tablename)
  INTO published_tables
  FROM pg_publication_tables AS ppt
  WHERE ppt.pubname = publication_name
    AND ppt.schemaname = schema_name;

  published_tables := COALESCE(published_tables, ARRAY[]::text[]);

  SELECT array_agg(t ORDER BY t)
  INTO missing
  FROM unnest(required) AS t
  WHERE NOT t = ANY(published_tables);

  IF array_length(missing, 1) IS NOT NULL THEN
    RAISE EXCEPTION 'RADAR_REALTIME_TABLE_MISSING: missing required table(s): %', missing USING ERRCODE = 'P0002';
  END IF;

  SELECT array_agg(t ORDER BY t)
  INTO unexpected
  FROM unnest(published_tables) AS t
  WHERE NOT t = ANY(required);

  IF array_length(unexpected, 1) IS NOT NULL THEN
    RAISE EXCEPTION 'RADAR_REALTIME_UNEXPECTED_PUBLISHED_TABLES: unexpected published table(s) in schema "%": %', schema_name, unexpected USING ERRCODE = 'P0003';
  END IF;

  RAISE NOTICE 'RADAR_REALTIME_PUBLICATION_OK: publication "%" for schema "%" contains exactly the expected tables', publication_name, schema_name;
END
$$;
