# Vera Provider Routing V1

Status: SOURCE CANDIDATE / STACKED ON FREEDOM V1 / NO PROVIDER EFFECT.

## Purpose

Select an execution route from explicit provider/model/adapter choices without
turning availability, capability, price, locality, or permissiveness into implied
user preference or effect authority.

## Exact route identity

A route is the exact tuple:
- provider_id
- model_id
- adapter_version

Provider id alone is insufficient. A different model or adapter is a different
route and must appear explicitly in policy.

## Policy semantics

`ProviderRoutePolicy.ordered_routes` is explicit ordered preference.

Selection rules:
1. routes not listed in policy are ignored;
2. manifests missing any required envelope capability are INELIGIBLE;
3. among listed routes, the first fully ELIGIBLE route wins;
4. DEGRADED routes are considered only when no ELIGIBLE route exists;
5. DEGRADED selection requires `allow_degraded=true`;
6. missing required capabilities never become DEGRADED merely because degraded
   routing is allowed;
7. duplicate exact-route manifests or duplicate policy routes fail closed.

This prevents an earlier degraded route from silently displacing a later fully
eligible route.

## Non-promotion rules

Routing does not grant:
- merge/deploy/provider/credential authority;
- permission to incur cost;
- permission to execute a provider request;
- permission to weaken the portable execution envelope;
- permission to select an unlisted local or less-restricted provider;
- proof that a provider manifest is independently authoritative.

A selection result carries the bounded claim:
`ROUTE_SELECTION_ONLY_NO_EFFECT_AUTHORITY`.

## Dependency

This layer is stacked on Freedom V1 provider portability. A route decision is only
meaningful for the exact envelope and manifest digests it contains. Movement of
the underlying portability subject creates a new downstream review subject.

No provider call, provider configuration, paid compute, credential use, merge,
deploy, or runtime cutover is performed by this candidate.
