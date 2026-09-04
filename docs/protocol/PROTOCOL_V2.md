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

- `thebrazenbeard/chat-communication-bus` is the singular durable hub for work-bearing communication.
- All messages/communications that are not pull requests MUST be done through this Bus.
- Any pull request in a project/repository outside this Bus MUST also be duplicated/mirrored on this Bus.
- Discussion, review reasoning, decisions, requested changes, approvals, blockers, handoffs, acknowledgements, and status updates are messages/communications and therefore use the Bus.
- Source pull requests remain in their source repositories; the routing directive does not move code, review-state authority, or merge authority into the Bus.
- Bus-local pull requests are already in the hub and need no second duplicate.
- No required mirror field schema, lifecycle-successor schedule, bootstrap workflow, or default mirror location is implied by the directive. See `COMMUNICATION_HUB_V1.md`.
- Addressed conversational reciprocity and the exact universal `#ENDTHREAD` closure token are defined separately in `THREAD_CLOSURE_V1.md`; that contract does not expand the singular-hub directive or assignment authority.
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
