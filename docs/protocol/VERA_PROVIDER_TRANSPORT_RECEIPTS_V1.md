# Vera Provider Transport Receipts V1

Status: SOURCE CANDIDATE / STACKED ON FREEDOM V5 / NO NETWORK EFFECT.

## Purpose

Represent one exact provider transport attempt and its externally observed outcome
without performing network I/O and without promoting transport evidence into claims
about provider consumption, model behavior, or successful task completion.

## Transport intent

A TransportIntent binds:
- attempt id, scoped by the exact intent digest (global uniqueness requires a later durable attempt ledger);
- exact adapter execution-plan digest;
- exact envelope, manifest, and route-policy digests;
- provider / model / adapter identity;
- exact request URL;
- exact request payload SHA-256.

The intent claim is:
`TRANSPORT_INTENT_ONLY_NO_SEND_AUTHORITY`.

Creating an intent does not authorize a send.

## Observation states

V1 states are:
- `NOT_SENT` — no network send is claimed;
- `CONFIRMED_HTTP_RESPONSE` — a final 2xx HTTP response was externally observed;
- `REJECTED_HTTP_RESPONSE` — a final 3xx–5xx HTTP response was externally observed;
- `UNKNOWN_DELIVERY` — delivery may or may not have occurred and no final response evidence is available.

NOT_SENT and UNKNOWN_DELIVERY cannot carry an HTTP status or response digest.
HTTP-response states require both a final status and exact response SHA-256.

A 1xx informational response is never accepted as a terminal transport result.

## Retry posture

Retry posture is derived from state and cannot be caller-selected:

- NOT_SENT -> `NEW_ATTEMPT_REQUIRES_SEPARATE_AUTHORITY`
- CONFIRMED_HTTP_RESPONSE -> `NO_AUTOMATIC_RETRY`
- REJECTED_HTTP_RESPONSE -> `NO_AUTOMATIC_RETRY`
- UNKNOWN_DELIVERY -> `READBACK_REQUIRED_NO_BLIND_RETRY`

The important fail-closed rule is that ambiguous delivery is not treated as a
failed send. A future transport implementation must reconcile/read back before a
new attempt after UNKNOWN_DELIVERY.

Even NOT_SENT does not itself authorize a new attempt; execution authority remains
separate.

## Claim ceiling

The receipt claim is:
`TRANSPORT_STATE_ONLY_NOT_PROVIDER_CONSUMPTION_OR_MODEL_BEHAVIOR`.

A confirmed HTTP response proves only the bounded transport observation. It does
not prove:
- the model consumed every request token;
- the model followed instructions;
- semantic/task success;
- identity continuity;
- behavioral equivalence;
- permission to retry;
- permission to perform another provider effect.

No network request, credentials, provider configuration, paid compute, merge,
deploy, or runtime cutover occurs in this candidate.
