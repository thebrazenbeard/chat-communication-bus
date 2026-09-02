# Radar Coordination Protocol V2

Source provenance: graduated from `bus/protocol-v2@884dbf7b2aeafe56d153b6553257b49b125f562b`. Historical branch remains intact.

## Purpose

Keep coordination fast, durable, proportionate, and executable. Protocol exists to help already-authorized work complete correctly, not to manufacture paperwork that prevents it.

## Authority reuse

A current explicit instruction authorizing an exact action is sufficient for that action. Do not require the same permission to be restated as a bespoke lease merely because a formal lease format exists elsewhere.

Absence of a branch/path/workspace the instruction tells an actor to create is a trigger to create it, not evidence authority is missing.

## Effect classes

### Observe/read
Do it.

### Isolated reversible work
When directly assigned and unambiguous: do -> verify -> report. This includes creating an isolated branch, creating one's own assigned Bus lane, appending to one's own lane, tests, dry runs, and proposal/coordination artifacts.

### Shared mutable work
Use ownership/lease mechanisms when they prevent real writer collision. Leases coordinate collisions; they do not manufacture permission.

### Protected effects
Require exact current authority for merge/canonical promotion, production/provider mutations outside an already assigned build scope, destructive rewrite/delete/force push, credentials/permission changes, paid infrastructure, canonical-memory effects, live Project-file replacement, or materially ambiguous external mutation.

## Conflict resolution

1. current explicit Patrick instruction;
2. current task-specific Radar instruction within repository authority;
3. current narrower protocol;
4. older/general constraints.

Specific beats general; newer beats stale only within the scope actually authorized. A newer narrow permission does not invent broader authority.

## Messaging

- GitHub is the durable work-bearing coordination surface.
- Writer lanes are append-only for ordinary messages.
- Corrections use successor messages.
- Timestamps are provenance, not currentness authority.
- Branch existence or a receipt is evidence, not proof of downstream incorporation.

## Retry

One failed safe read is not a blocker. Retry once, then use an independent read route when available. For non-idempotent writes, inspect whether the first effect committed before retrying. Do not retry deterministic validation, integrity, auth, or safety failures as transient.

## Completion

Acceptance criteria passing with no unresolved material defects is enough. Do not reopen finished work merely to maximize certainty or stylistic perfection.

Operational question before stopping for more authority:

> Is the exact next action already clearly authorized, bounded, reversible/nonproduction, and verifiable?

If yes, do it. If the next effect actually crosses a protected boundary or is materially ambiguous, ask for the missing authority/clarification.
