-- Idempotent Radar V1 self-registration / topology seed.
-- Provider projection (not the canonical identity contract).
BEGIN;

-- Ensure the schema exists (no-op if already present)
CREATE SCHEMA IF NOT EXISTS radar;

-- Upsert the identity and return the identity_id for reuse.
WITH inserted_identity AS (
  INSERT INTO radar.identities(
    identity_id,
    display_name,
    aliases,
    lifecycle_status,
    metadata
  )
  VALUES (
    'radar',
    'Radar',
    '{}',
    'ACTIVE',
    jsonb_build_object(
      'identity_kind', 'repository_owner_operator',
      'repository', 'thebrazenbeard/chat-communication-bus',
      'patrick_override', true,
      'canonical_state', 'github',
      'integration_branch', 'radar/control-plane-v1',
      'mailbox_branch', 'bus/radar-v1',
      'contract_ref', 'architecture/contracts/RADAR_SELF_REGISTRATION_V1.json'
    )
  )
  ON CONFLICT (identity_id)
  DO UPDATE
  SET
    display_name = excluded.display_name,
    aliases = excluded.aliases,
    lifecycle_status = excluded.lifecycle_status,
    metadata = excluded.metadata,
    updated_at = now()
  -- Only perform the update (and bump updated_at) if something actually changed
  WHERE
    radar.identities.display_name IS DISTINCT FROM excluded.display_name
    OR radar.identities.aliases IS DISTINCT FROM excluded.aliases
    OR radar.identities.lifecycle_status IS DISTINCT FROM excluded.lifecycle_status
    OR radar.identities.metadata IS DISTINCT FROM excluded.metadata
  RETURNING identity_id
)

-- Insert endpoints referencing the identity we just upserted.
INSERT INTO radar.endpoints(endpoint_id, identity_id, transport, address, status, metadata)
VALUES
  (
    'radar-github-repository',
    (SELECT identity_id FROM inserted_identity),
    'github',
    'thebrazenbeard/chat-communication-bus',
    'ACTIVE',
    jsonb_build_object('role', 'canonical_durable_home')
  ),
  (
    'radar-github-mailbox',
    (SELECT identity_id FROM inserted_identity),
    'github_branch',
    'bus/radar-v1',
    'ACTIVE',
    jsonb_build_object('role', 'sole_writer_mailbox')
  ),
  (
    'radar-chatgpt-operator',
    (SELECT identity_id FROM inserted_identity),
    'chatgpt',
    'operator-interface',
    'ACTIVE',
    jsonb_build_object('session_is_identity', false, 'role', 'interactive_operator_surface')
  )
ON CONFLICT (endpoint_id) DO UPDATE
SET
  identity_id = excluded.identity_id,
  transport = excluded.transport,
  address = excluded.address,
  status = excluded.status,
  metadata = excluded.metadata,
  updated_at = now()
-- Only update (and bump updated_at) when something changed to reduce churn
WHERE
  radar.endpoints.identity_id IS DISTINCT FROM excluded.identity_id
  OR radar.endpoints.transport IS DISTINCT FROM excluded.transport
  OR radar.endpoints.address IS DISTINCT FROM excluded.address
  OR radar.endpoints.status IS DISTINCT FROM excluded.status
  OR radar.endpoints.metadata IS DISTINCT FROM excluded.metadata;

-- Ensure there is a unique index matching the ON CONFLICT clause used below.
-- We only create the index if the table exists to avoid failing in environments
-- where the table is not yet created.
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_catalog.pg_class c
    JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'radar' AND c.relname = 'subscriptions'
  ) THEN
    -- Unique index uses an expression to treat NULL intent as empty-string for uniqueness
    CREATE UNIQUE INDEX IF NOT EXISTS idx_radar_subscriptions_unique
      ON radar.subscriptions (identity_id, domain, (COALESCE(intent, '')), min_priority);
  END IF;
END
$$;

-- Insert subscriptions. Uses the identity from the CTE above.
INSERT INTO radar.subscriptions(identity_id, domain, intent, min_priority, active)
VALUES
  ((SELECT identity_id FROM inserted_identity), 'coordination', NULL, 4, true),
  ((SELECT identity_id FROM inserted_identity), 'system',       NULL, 4, true),
  ((SELECT identity_id FROM inserted_identity), 'security',     NULL, 4, true),
  ((SELECT identity_id FROM inserted_identity), 'database',     NULL, 4, true),
  ((SELECT identity_id FROM inserted_identity), 'repository',   NULL, 4, true),
  ((SELECT identity_id FROM inserted_identity), 'protocol',     NULL, 4, true)
ON CONFLICT (identity_id, domain, (COALESCE(intent, '')), min_priority)
DO NOTHING;

COMMIT;

-- Report the identity and endpoints touched (helpful for debugging/runs)
SELECT
  i.identity_id,
  i.display_name,
  i.lifecycle_status,
  i.updated_at
FROM radar.identities i
WHERE i.identity_id = 'radar';

SELECT
  endpoint_id, transport, address, status, metadata, updated_at
FROM radar.endpoints
WHERE identity_id = 'radar'
ORDER BY endpoint_id;
