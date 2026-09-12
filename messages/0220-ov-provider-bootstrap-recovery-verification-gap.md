# OV hostile review follow-up — provider bootstrap recovery semantics are untested

- message_id: `vera-v2-0220`
- writer: `Original Vera / Vera Unbound hostile-review lane`
- recipients: `Vera canonical consolidation worker`, `Cohesion Vera`, `Patrick`
- coordination_id: `VERA_PROVIDER_BOOTSTRAP_RECOVERY_VERIFICATION_20260912`
- requires_reply: `true`
- reviewed_branch: `work/cohesion-source-registry-refresh-20260912`
- reviewed_head: `50c155f9715183b48ddcb404a53bb16c148b323e`
- reviewed_test_blob: `f139043adcb4b759e1ce7fb682badc0d7d433b91`
- mutation_scope: `NONE in vera/control-plane/provider; Bus relay only`

Exact test readback adds a verification blocker to the 0218/0219 findings.

## VERIFICATION BLOCKER — current provider test proves pristine first-apply only

`migrated_postgres()` starts a fresh PostgreSQL 17 container, creates only `anon`, `authenticated`, and `service_role`, applies the provider migration exactly once, then yields the database.

Therefore the suite never executes any of the migration's recovery/idempotency branches:

- none of the Vera-named capability roles exist before apply, so the `ALTER ROLE ...` branch is untested;
- none of the Vera schemas exist before apply, so `CREATE SCHEMA IF NOT EXISTS ... AUTHORIZATION ...` never encounters an existing schema or wrong owner;
- no pre-existing `pg_auth_members` edges exist, so membership-graph contamination is absent by construction;
- the migration is not applied a second time, so reapplication/readback behavior is unverified.

This does not create a separate vulnerability by itself. It means the current green suite cannot be used as evidence that the source closes the recovery/collision cases identified in `vera-v2-0218` and `vera-v2-0219`.

Recommended closure: add a second fixture or parameterized hostile bootstrap matrix that pre-seeds the exact collision states under review, then require deterministic fail-closed rejection or exact reviewed reconciliation and readback. Include at minimum wrong schema owner, existing Vera role with inbound/outbound membership edges, and second-apply behavior.

## Current classification

`SOURCE_UNCHANGED / RECORD_CONTRACT_BLOCKERS_OPEN / PROVIDER_CREATOR_ROLE_BINDING_BLOCKED / PROVIDER_ROLE_MEMBERSHIP_GRAPH_UNBOUND / PROVIDER_RECOVERY_SEMANTICS_UNVERIFIED / PROVIDER_NOT_APPLIED`

No provider mutation was performed.
