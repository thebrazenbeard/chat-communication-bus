# ADR-0005 — Assignment Runtime-Instance Fencing

Status: `DESIGN_ONLY / NOT_INSTALLED / ISSUE_142`

Exact design base:
- repository: `thebrazenbeard/chat-communication-bus`
- active Exodus integration subject: PR #140
- exact head: `2461df3a1a8393d4c7ded227afb17ecc7abfacb3`

This ADR is source design only. It adds no migration, applies no database change, activates no runtime path, and grants no protected-effect authority.

## Problem

The durable assignment projection binds work to `assignee_identity_id`. The node-routing layer separately gives each runtime a `node_id`, an immutable durable-identity owner, heartbeat state, and a lease.

After the Exodus, two ephemeral runtimes may legitimately reconstruct the same durable worker identity at the same time. Both can therefore see the same identity-level assignment. Existing predecessor-bound assignment events prevent assignment-history forks, but they do not establish which live runtime instance currently owns execution.

This is an execution-collision/stale-worker problem, not an identity or user-authority problem.

## Decision

Add a runtime-only execution-claim layer between assignment ownership and node liveness.

The assignment continues to belong to the durable worker identity. A claim says only which live runtime generation may currently execute that assignment.

The claim key is the assignment. The claim value binds:
- assignment;
- durable assignee identity;
- live node;
- monotonically comparable fence token;
- exact current assignment event used as the execution subject;
- bounded lease;
- idempotency operation;
- update time.

Maintain append-only claim-generation/audit evidence beside the current projection. Current ownership may change; the generation history must not be overwritten away.

## Acquire

Acquisition must serialize per assignment and fail closed unless all are true:

1. assignment exists;
2. node exists;
3. node identity exactly equals the assignment assignee identity;
4. node is in a live/routable status and its node lease has not expired;
5. assignment dependency readiness is satisfied;
6. the exact current assignment event is captured as the claim subject;
7. requested claim lease does not outlive the node lease.

If another unexpired valid holder exists, acquisition fails closed.

A takeover after expiry/invalidation allocates a strictly newer fence token. Token gaps are acceptable; token reuse is not.

A retry is idempotent only within the exact namespace `(assignment_id, operation_kind, operation_id)`. Reusing the same `operation_id` for a different assignment or a different operation kind is a distinct operation and must not alias a prior result. A retry with the same full namespace key returns the already-recorded result rather than allocating another generation.

## Renew

Renewal requires the same current node, fence token, and bound assignment event. It does not allocate a new token. The renewed claim still may not outlive the node lease.

## Assignment advancement

Any runtime-authored assignment successor must carry:
- execution node id;
- execution fence token;
- assignment event id on which execution was based.

Reconciliation accepts the successor only when the claim is still current and all three bindings match.

A stale runtime cannot complete work after takeover merely because it still knows the durable identity or old assignment.

When the valid holder advances the assignment, reconciliation may roll the claim's bound event forward in the same transaction.

When another authorized control-plane actor advances or supersedes the assignment, the prior execution claim is invalidated/released. The control-plane transition does not transfer runtime ownership implicitly.

## Authority

An execution claim coordinates one runtime generation. It does not create or expand:
- merge authority;
- deployment authority;
- provider/database mutation authority;
- credential/permission authority;
- protected-effect authority.

Durable assignment authority and Patrick's protected-effect gates remain separate.

## Security boundary

Future mutating claim functions are service-role-only. `public`, `anon`, and `authenticated` must not receive execute permission. The implementation must persist or enforce idempotency with a collision-proof uniqueness key over `assignment_id`, `operation_kind`, and `operation_id` (or an equivalent exact namespace with the same semantics).

This ADR does not authorize application of any future migration.

## Required hostile qualification

A future implementation must reproduce and pass all hostile cases named in `architecture/contracts/ASSIGNMENT_EXECUTION_CLAIM_V1.json`.

Especially:
- two same-identity nodes racing;
- stale loser continuing;
- takeover after expiry;
- old-token replay after takeover;
- assignment change while claim held;
- lost-response idempotency;
- dependency-readiness bypass attempts;
- identity mismatch;
- lease extending past node lease;
- attempts to convert a claim into protected-effect authority.

## Rejected alternatives

### Put node_id on the durable worker identity

Rejected. It collapses durable identity into one runtime instance and defeats the Exodus execution-terminal model.

### Treat node lease alone as assignment ownership

Rejected. A live node lease proves node liveness, not ownership of one particular assignment generation.

### Treat assignment predecessor checks alone as fencing

Rejected. They serialize durable assignment history but do not stop two same-identity runtimes from doing duplicate external work before either publishes a successor.

### Make claim acquisition grant authority

Rejected. Fencing is execution coordination only.

## Implementation gate

Before implementation:
1. fresh-check the active Bus integration line;
2. preserve the current assignment and node hardening invariants;
3. freeze RED hostile cases on the exact implementation parent;
4. implement the smallest forward-only source migration and service-role API;
5. run source/SQL qualification on the exact candidate;
6. do not apply the migration or deploy without separate current authority.
