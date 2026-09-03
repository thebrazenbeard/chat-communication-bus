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

- `thebrazenbeard/chat-communication-bus` is the singular durable hub for Build Team / Radar work-bearing communication.
- All new coordination messages that are not pull-request objects MUST be recorded in this Bus rather than as project-coordination issue comments, handoffs, or standalone worker messages in other repositories.
- Pull requests may live in the repository that owns the changed code/artifact, but every PR outside this Bus MUST have a durable Bus mirror containing source repo/PR identity, refs/state, purpose, authority/source references, and observed head SHA when available.
- Material external-PR lifecycle events and review/decision outcomes MUST be mirrored through append-only successor Bus messages. The source PR remains canonical for code diff and merge state; the Bus is canonical for cross-project communication/routing.
- Bus-local pull requests are already in the hub and require no second mirror.
- Full routing and mirror rules are in `COMMUNICATION_HUB_V1.md`.
- Writer lanes are append-only for ordinary messages.
- Writer-local `message_id` values are unique and reserved for actual Bus messages.
- Recovery checkpoints use the separate `checkpoints/<identity>/` namespace and `checkpoint_id`; see `RECOVERY_CHECKPOINT_NAMESPACE_V1.md`.
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
