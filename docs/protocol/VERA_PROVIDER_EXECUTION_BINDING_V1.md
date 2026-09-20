# Vera Provider Execution Binding V1

Status: SOURCE CANDIDATE / STACKED ON FREEDOM V2 / NO PROVIDER EFFECT.

## Purpose

Close the seam between provider route selection and provider-specific submission.

A route decision for one provider/model/adapter must not be reusable to prepare
material for another route, another execution envelope, or a different manifest.

## Preparation boundary

`prepare_adapter_execution()` requires:
- the exact portable execution envelope;
- the exact provider manifest selected by the route decision;
- a selected route decision (never NO_ROUTE);
- raw instruction text and task input bytes;
- exact state blob bytes;
- the concrete GitHub provenance resolver.

It then:
1. verifies route decision envelope and manifest digests;
2. verifies exact provider + model + adapter identity;
3. rejects NO_ROUTE and INELIGIBLE qualification;
4. re-runs authoritative GitHub provenance and exact-byte materialization;
5. requires materialized qualification to match route qualification;
6. emits an adapter execution plan bound to policy/envelope/manifest digests,
   state blobs, prohibited effects, and authority scope.

## Claim boundary

The plan carries:
`ADAPTER_BINDING_ONLY_NO_PROVIDER_EXECUTION_AUTHORITY`

It is a pre-submission binding artifact. It does not:
- call a provider;
- authorize provider execution;
- authorize cost;
- override prohibited effects;
- prove a provider consumed or obeyed submitted material;
- establish behavioral equivalence or identity continuity.

Provider-specific adapters should build from this boundary rather than accepting a
route key and arbitrary prompt/state bytes independently.

No provider call, provider configuration, credentials, paid compute, merge,
deploy, or runtime cutover occurs in this candidate.
