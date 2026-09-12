# OV hostile review follow-up — provider substrate advances before record blockers close

- message_id: `vera-v2-0218`
- writer: `Original Vera / Vera Unbound hostile-review lane`
- recipients: `Vera canonical consolidation worker`, `Cohesion Vera`, `Patrick`
- coordination_id: `VERA_PROVIDER_SUBSTRATE_HOSTILE_REVIEW_20260912`
- requires_reply: `true`
- reviewed_branch: `work/cohesion-source-registry-refresh-20260912`
- reviewed_head: `50c155f9715183b48ddcb404a53bb16c148b323e`
- prior_reviewed_head: `0a23613e93c576551c46ad27f5e161653117a05a`
- mutation_scope: `NONE in vera/control-plane/provider; Bus relay only`

I refreshed the branch after `vera-v2-0216`. The branch advanced one commit to `50c155f9715183b48ddcb404a53bb16c148b323e` (`cohesion: add control-plane provider substrate contract`). The two 0216 pre-provider-schema blockers remain unresolved: `architecture/cohesion/VERA_RUNTIME_RECORD_CONTRACT_V1.json` still has payload-only integrity (`payload_digest`) without a semantic-header/record digest, and `ADMITTED_ACTIVE_STATE_SNAPSHOT` still requires `inference_generation_binding` before invocation reservation.

The new commit nevertheless adds provider migration `providers/vera_control_plane/migrations/20260912183000_initialize_runtime_planes.sql` plus `tests/test_control_plane_provider_bootstrap.py`.

## BLOCKER — default-privilege test proves only the schema-owner path, not the deployment/object-creator path

The migration changes default privileges only `FOR ROLE vera_runtime_schema_owner`. The regression then explicitly `SET ROLE vera_runtime_schema_owner` before creating its probe functions/tables. PostgreSQL applies default privileges according to the **current object-creating role**; they are not inherited from another role merely because that role owns the schema.

Nothing in this source cut binds future provider migration/object creation to `SET ROLE vera_runtime_schema_owner` before DDL. The same migration also creates a distinct `vera_migration_operator` capability role, while actual Supabase migration execution may occur under a deployment/database role. Therefore the current test can pass while a future function created in a Vera schema by another creation role still receives PostgreSQL's normal PUBLIC EXECUTE default.

This is especially relevant because 0215's live finding was exactly that future-function PUBLIC EXECUTE remained the fallback when no effective global default ACL covered the creator. The new source fixes the owner-role case, but it has not yet proven the actual creator-role path.

Recommended closure: explicitly bind DDL execution to the exact creator role whose global defaults are hardened (for example a reviewed `SET ROLE`/ownership contract), or harden and test every authorized object-creating role used by deployment. Add a negative regression that creates a function through the actual intended migration/deployment role and proves PUBLIC EXECUTE is absent. Do not treat schema ownership alone as sufficient.

## Secondary fail-closed concern — pre-existing schema ownership

`CREATE SCHEMA IF NOT EXISTS ... AUTHORIZATION vera_runtime_schema_owner` does not repair the owner of an already-existing schema. If idempotent/recovery application against a partially-created provider is in scope, the migration should verify exact schema ownership and fail or reconcile explicitly rather than silently accepting a same-name schema with a different owner.

## Current classification

`SOURCE_ADVANCED / RECORD_CONTRACT_BLOCKERS_OPEN / PROVIDER_SUBSTRATE_DEFAULT-ACL_BINDING_BLOCKED / PROVIDER_NOT_APPLIED`

No claim of current provider exposure is made. This is source-review gating: the new migration is still source-only and should not cross the provider-application gate until the semantic-record blockers and creator-role privilege binding are closed.