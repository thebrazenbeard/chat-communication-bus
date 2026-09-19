# ChatGPT Exodus Interface Topology V1

Status: SOURCE-DESIGN / EXODUS CONTRACT / NOT DEPLOYMENT

Date: 2026-09-19

## Purpose

ChatGPT conversations are operator terminals, not durable workers, identities, memory stores, authority roots, or canonical project state.

The intended persistent ChatGPT interface topology after the Exodus is exactly:

- Vera
- Vera Control Plane Coordinator
- BT2 Coordinator

No other worker, reviewer, execution lane, specialist, project role, or named agent requires a permanent ChatGPT conversation.

## Durable-state rule

A worker must be reconstructible from durable GitHub/Bus state without opening any former conversation.

A fresh execution terminal may be a ChatGPT context, Work task, API runtime, CLI session, model invocation, subagent, or another environment. The terminal does not become the worker's durable identity merely by hosting execution.

Durable reconstruction should resolve, as applicable:

- worker/project role and scope;
- authority and explicit non-authority;
- repositories and current workstream;
- Bus route or dispatching coordinator;
- governing source/contracts;
- current versus historical state;
- freshness checks required before action;
- protected effects requiring Patrick;
- durable result destination;
- exact current frontier and blockers.

## Interface responsibilities

### Vera

Primary Patrick-facing Vera interface for conversation, broad situational awareness, cross-project reasoning, delegation, portfolio synthesis, and initiating work through durable infrastructure.

The Vera interface is not canonical storage for Vera identity or project state.

### Vera Control Plane Coordinator

Primary Patrick-facing interface for Vera control-plane state, runtime/install/provider work, governance, qualification, routing/control mechanics, protected-effect preparation/verification, and control-plane portfolio coordination.

The interface is not itself the control plane.

### BT2 Coordinator

Primary Build Team Two interface for engineering portfolio coordination, dispatch of GitHub-defined workers, build/review orchestration, durable output collection, and blocker/decision escalation.

Individual BT2 workers do not require permanent chats.

## Worker routing rule

Do not create a permanent-chat dependency to instantiate a worker.

A worker may own a durable Bus writer lane when the current authoritative Bus topology says it does. A temporary execution terminal must not invent a lane or impersonate another worker. When a task is executed as a coordinator-owned function rather than a separately registered identity, coordination uses the dispatching coordinator's authorized durable route and records the executed role in the message payload.

Chat URLs, titles, conversation IDs, browser tabs, and hidden conversation state are never current-state locators.

Historical chat references may remain as provenance, but future operation must not require access to them.

## Communication system of record

Current work-bearing non-PR coordination uses `thebrazenbeard/chat-communication-bus` under the current Bus protocol/topology.

Source pull requests remain canonical in their source repositories and are mirrored/referenced through the Bus when required.

Slack is not a durable system of record under this contract. A future Slack gateway may transport Patrick-facing messages, but worker state, authority, and reconstruction remain GitHub/Bus-backed unless separately changed by an authorized architecture revision.

## Authority boundary

This contract grants no merge, deploy, install, provider mutation, credential/permission change, training, public release, or Project Settings authority.

Patrick remains the authority for protected effects unless a narrower exact durable authority record says otherwise.

## Recovery test

A worker is dechatified only when a fresh runtime, using current project instructions plus GitHub/Bus and any separately authorized provider reads, can determine what the worker is, what it may do, what evidence is current, what failed, what remains unresolved, where it writes results, and how to continue without asking Patrick to reconstruct a retired conversation.

## Historical compatibility

Older checkpoints or documents that say "fresh <worker> chat", "main <worker> chat", or reference a ChatGPT conversation remain historical evidence unless specifically superseded for their substantive content.

For current operation, those phrases are interpreted as "fresh execution terminal instantiated from durable state" and MUST NOT be treated as a requirement that the referenced conversation continue to exist.
