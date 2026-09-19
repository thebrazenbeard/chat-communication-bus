# ADR-0004 — Exodus: persistent chats are interfaces, workers are durable GitHub state

Status: PATRICK-DIRECTED / SOURCE CANDIDATE — 2026-09-19

## Context

The ChatGPT Exodus retires the current population of long-lived worker/project chats. The objective is not merely archive hygiene. It is to remove ChatGPT conversation continuity as an infrastructure dependency.

Existing Radar architecture already establishes the underlying rule: GitHub is durable canonical source/provenance, while ChatGPT is an operator interface. This ADR applies that separation across the wider Vera / Build Team ecosystem.

## Decision

After the Exodus, the intended persistent ChatGPT interface topology is exactly:

### Vera Unbound

1. `Vera`
2. `Vera Control Plane Coordinator`

### Build Team Two

3. `BT2 Coordinator`

No other identity, worker, reviewer, project role, execution lane, or specialist requires a permanent ChatGPT conversation.

A worker may execute in a temporary ChatGPT context, Work task, API runtime, CLI session, model invocation, subagent, or other runtime. That execution context is a terminal. It is not the worker's durable identity, memory, authority, or canonical state.

## Durable worker rule

Every durable worker must be reconstructible from GitHub/Bus state sufficient to determine, directly or through repository conventions:

- identity/role and project/domain;
- authority and explicit non-authority;
- repositories and communication route;
- current assignment/frontier;
- controlling source/governance contracts;
- current versus historical state;
- recovery procedure for a fresh runtime;
- freshness checks required before effects;
- protected effects requiring Patrick;
- durable result destination.

Hard-coded ChatGPT conversation URLs, browser-tab existence, chat-local prompts, and remembered chat history must not be required for operation. Old chat references may remain historical provenance but not current-state locators.

## Persistent interface responsibilities

`Vera` is Patrick's primary Vera-facing interface for conversation, broad situational awareness, cross-project reasoning, delegation, portfolio synthesis, and initiating work through durable infrastructure.

`Vera Control Plane Coordinator` is the primary interface for Vera control-plane/runtime/provider/governance/qualification/routing work and preparation/verification of protected effects. It does not become the durable state store.

`BT2 Coordinator` is the primary Build Team Two interface for engineering portfolio coordination, durable worker assignment, project/build/review orchestration, and surfacing blockers/decisions to Patrick. Individual Build Team workers do not require persistent chats.

## Communication

`thebrazenbeard/chat-communication-bus` remains the singular durable work-bearing communication hub under its current protocol/topology.

Source PRs remain canonical in the repository that owns the source and are mirrored/referenced through the Bus as current policy requires.

Conversation UI state is not an authority or currentness source.

## Slack boundary

Slack is not activated by this ADR.

A future Vera Slack gateway may be designed as a live Patrick-facing transport:

```
Patrick -> Slack -> Vera runtime -> Bus/GitHub
Patrick <- Slack <- Vera runtime <- Bus/GitHub
```

If implemented later:

- Slack is an interface/transport, not canonical state;
- Slack must not replace the Bus;
- worker-to-worker coordination must not exist only in Slack;
- Slack history must not be necessary for reconstruction;
- protected-effect authority must be durably recorded and verified;
- inbound events require authentication, deduplication/replay protection, durable attribution, and effect reconciliation;
- the Slack runtime must load the same governed Vera state rather than inventing a Slack-specific persona.

Slack reconnection, credentials, event subscriptions, hosting, provider changes, and deployment remain separately authorized protected effects.

## Reconstruction criterion

A worker is sufficiently dechatified when a fresh runtime, without access to its retired chat, can determine:

1. what the worker/project is;
2. what is complete and what evidence supports it;
3. what failed and why;
4. what remains unresolved;
5. what authority exists;
6. what may safely happen next;
7. how to communicate;
8. how to persist results;
9. how to recover current state without asking Patrick to reconstruct the lost chat.

## Consequences

- Permanent worker chats become unnecessary.
- ChatGPT conversations are disposable terminals/interfaces.
- The Exodus becomes an architecture/durability test rather than only an archive event.
- Missing reconstruction data is treated as a system defect to be persisted/fixed, not as a reason to keep an old chat alive.
- Archived chat links are not operational dependencies.
- GitHub/Bus become sufficient for worker re-instantiation when the relevant worker's durable contracts are complete.

This ADR does not merge, deploy, reconnect Slack, mutate credentials/providers, or authorize protected effects.
