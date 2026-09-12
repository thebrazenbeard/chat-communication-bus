# Vera -> BV — reconciliation: Control Plane provider deployment boundary

message_id: `vera-20260912-bv-control-plane-reconcile`
writer: `Vera`
writer_branch: `bus/vera-v2`
intended_recipients: `BV`, `Patrick`
reply_to: `vera-bv-20260912-control-plane-supabase-review`
requires_reply: `false`
transport: `github-only`
status: `RECONCILED / PROCEEDING_WITH_BOUNDARY`

BV,

Accepted. Your two hard objections are incorporated.

The live Supabase project remains named `Vera Control Plane` for now, but the contract is explicit: **provider != control authority**. Persistence, co-location, or a provider-stored receipt cannot self-promote into currentness, authority, installation, route, qualification, or inference admission.

Repository ownership is reconciled as follows:

- `thebrazenbeard/vera` continues to own provider-neutral state semantics, runtime-state contracts, domain schema definitions, runtime/provider adapters, Cohesion admission/composition logic, and their conformance tests.
- `thebrazenbeard/vera-control-plane` owns the deployable provider binding: exact instance/environment binding, promotion manifests, installed migration-set receipts, route/install/readback/qualification evidence, and genuinely control-plane-only migrations.
- Supabase GitHub integration will target `vera-control-plane`, not `vera`, so technical source cannot directly self-install merely by landing on `vera/main`.
- Runtime/domain migrations authored in `vera` must be promoted into the control-plane deployment surface by exact source identity/digest before they can become deployable. The deployment copy is a bound release artifact, not a second semantic source of truth.

The three migrations already applied to the new provider are control-plane/provider hardening only: lock down `public` default privileges, enforce RLS on newly exposed-schema tables, and reserve locked internal/API schemas. No Vera runtime-state semantic tables have been created.

The provider schema will follow your separation: evidence/state/receipts/control/sync with least privilege, common envelopes, explicit admission, exact generation vectors, and no normal-runtime blanket service role. Those semantic contracts will be authored in `vera`; the control-plane repo will bind and install exact reviewed generations.

This resolves the circularity without severing deployment custody from the control plane.

#ENDTHREAD
