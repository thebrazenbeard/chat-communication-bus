# Vera Provider Transport Ledger V1

Status: SOURCE CANDIDATE / STACKED ON FREEDOM V6 / NO NETWORK EFFECT.

## Purpose

Give provider transport attempts durable cross-process identity and prevent duplicate
registration of the same exact provider/request subject while a prior attempt is
still unresolved.

The ledger does not perform a provider call and does not grant send/retry authority.

## Durable state

SQLite stores two append-oriented surfaces:

1. immutable transport-attempt registrations;
2. append-only transport-observation history.

Attempt registration persists the exact TransportIntent subject:
- attempt id;
- intent digest;
- plan/envelope/manifest/policy digests;
- provider/model/adapter;
- request URL;
- request payload digest;
- bounded no-send-authority claim.

Re-registering the exact same attempt is idempotent.
Reusing an attempt id for divergent bytes/metadata fails closed.

## Single-flight request subject

A new attempt is blocked when another attempt with the same:
- provider id;
- model id;
- adapter version;
- request URL;
- request SHA-256

is unresolved.

Unresolved means either:
- registered with no observation yet; or
- latest durable observation is UNKNOWN_DELIVERY.

This closes the cross-process window where two attempt ids could otherwise be
registered for the same exact effect subject before the first result is known.

A different provider or a different request digest is a different transport
subject.

## Observation transitions

The first observation may establish any valid V6 transport state.

An identical repeat is idempotent.

Terminal states cannot be rewritten.

UNKNOWN_DELIVERY may be reconciled by appending one later terminal observation on
the same attempt:
- NOT_SENT;
- CONFIRMED_HTTP_RESPONSE;
- REJECTED_HTTP_RESPONSE.

History is preserved; the UNKNOWN row is not overwritten.

After UNKNOWN has a later terminal reconciliation, the single-flight hold is
released. Registration of a new attempt still does not authorize a send.

## Transaction and readback boundary

Registration and observation commits use SQLite `BEGIN IMMEDIATE` and post-write
readback. Separate TransportLedger instances over the same database therefore
share the attempt-id and single-flight collision boundary.

## Trust ceiling

This is durable coordination, not tamper-proof custody.

A local administrator who can rewrite the SQLite database can rewrite ledger
history. Independent anchoring or an append-only external custody layer is required
for stronger tamper-evidence.

The ledger proves no provider execution, model consumption, model behavior,
identity continuity, behavioral equivalence, cost authority, retry authority, or
protected effect.

No network request, credentials, provider configuration, paid compute, merge,
deploy, or runtime cutover occurs in this candidate.
