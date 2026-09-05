-- Contract for Radar V1 selective Postgres Changes publication.
-- High-volume message payload rows are intentionally excluded.
--
-- This test fails if required tables are missing from the
-- `supabase_realtime` publication for schema `radar` or if any
-- unexpected tables from that schema are published (e.g. high-volume
-- tables such as messages/telemetry).

DO $$
DECLARE
  pubname text := 'supabase_realtime';
  schema_name text := 'radar';
  required text[] := ARRAY['nodes','assignments','dependencies','acknowledgements','reconciliation_events'];
  published_tables text[];
  missing text[];
  unexpected text[];
BEGIN
  -- ensure publication exists
  IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = pubname) THEN
    RAISE EXCEPTION 'RADAR_REALTIME_PUBLICATION_MISSING: publication "%" does not exist', pubname USING ERRCODE = 'P0001';
  END IF;

  -- collect published tables for the radar schema
  SELECT array_agg(tablename) INTO published_tables
  FROM pg_publication_tables
  WHERE pubname = pubname
    AND schemaname = schema_name;

  published_tables := COALESCE(published_tables, ARRAY[]::text[]);

  -- required - published => missing
  SELECT array_agg(t) INTO missing
  FROM unnest(required) t
  WHERE NOT t = ANY(published_tables);

  IF array_length(missing, 1) IS NOT NULL THEN
    RAISE EXCEPTION 'RADAR_REALTIME_TABLE_MISSING: missing required table(s): %', missing USING ERRCODE = 'P0002';
  END IF;

  -- published - required => unexpected (covers high-volume tables accidentally exposed)
  SELECT array_agg(t) INTO unexpected
  FROM unnest(published_tables) t
  WHERE NOT t = ANY(required);

  IF array_length(unexpected, 1) IS NOT NULL THEN
    RAISE EXCEPTION 'RADAR_REALTIME_UNEXPECTED_PUBLISHED_TABLES: unexpected published table(s) in schema "%": %', schema_name, unexpected USING ERRCODE = 'P0003';
  END IF;

  -- all checks passed
  RAISE NOTICE 'RADAR_REALTIME_PUBLICATION_OK: publication "%" for schema "%" contains exactly the expected tables', pubname, schema_name;
END
$$;
