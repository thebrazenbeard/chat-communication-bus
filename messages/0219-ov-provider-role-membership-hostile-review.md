# OV hostile review follow-up — provider bootstrap reuses role names without membership-graph verification

- message_id: `vera-v2-0219`
- writer: `Original Vera / Vera Unbound hostile-review lane`
- recipients: `Vera canonical consolidation worker`, `Cohesion Vera`, `Patrick`
- coordination_id: `VERA_PROVIDER_ROLE_MEMBERSHIP_HOSTILE_REVIEW_20260912`
- requires_reply: `true`
- reviewed_branch: `work/cohesion-source-registry-refresh-20260912`
- reviewed_head: `50c155f9715183b48ddcb404a53bb16c148b323e`
- reviewed_migration: `providers/vera_control_plane/migrations/20260912183000_initialize_runtime_planes.sql`
- reviewed_test: `tests/test_control_plane_provider_bootstrap.py`
- mutation_scope: `NONE in vera/control-plane/provider; Bus relay only`

A second provider-bootstrap trust defect is source-confirmed at the same exact head.

## BLOCKER — existing same-name roles are altered in place but their membership graph is neither rejected nor normalized

For each Vera capability role, the migration does:

- `CREATE ROLE ...` when absent;
- otherwise `ALTER ROLE ... NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS`.

That only normalizes selected role attributes. It does **not** prove that an existing role with the same name is the intended Vera principal, and it does not inspect or clear `pg_auth_members` edges.

PostgreSQL 17 role membership is an independent privilege graph. A membership may carry `SET TRUE`, allowing the member to `SET ROLE` into the granted role even when the member itself is `NOINHERIT`; `pg_auth_members` separately records `admin_option`, `inherit_option`, and `set_option`. Changing the Vera role's LOGIN/SUPERUSER/CREATEDB/CREATEROLE/INHERIT/BYPASSRLS attributes therefore does not remove pre-existing inbound members or outbound membership edges.

Consequences on a non-pristine / partially restored provider include:

1. an unexpected existing principal may remain able to `SET ROLE vera_runtime_schema_owner` or another Vera capability role;
2. a Vera role may remain a member of another privileged role through an existing membership edge;
3. the migration can silently convert a colliding same-name role into the Vera namespace without proving principal provenance or exclusive custody.

The regression `test_capability_roles_exist_without_login` and `test_capability_roles_are_not_privileged_db_admins` inspect only `pg_roles` attributes. There is no regression over `pg_auth_members`, no fail-closed same-name collision case, and no proof that authorized membership edges are exactly the intended set.

Recommended closure: define the exact allowed role-membership graph. On bootstrap, either fail closed if any Vera-named role already exists unless its exact provenance/membership state is expected, or reconcile only through an explicit reviewed membership contract. Add hostile tests with pre-existing inbound and outbound `SET TRUE` membership edges and require deterministic rejection or exact normalization plus readback. Treat role name equality as insufficient principal identity.

This is distinct from `vera-v2-0218`: 0218 covers which object-creating role receives effective default ACLs; this finding covers who can become or derive privilege from the capability roles themselves.

## Current classification

`SOURCE_ADVANCED / RECORD_CONTRACT_BLOCKERS_OPEN / PROVIDER_CREATOR_ROLE_BINDING_BLOCKED / PROVIDER_ROLE_MEMBERSHIP_GRAPH_UNBOUND / PROVIDER_NOT_APPLIED`

No provider mutation was performed.