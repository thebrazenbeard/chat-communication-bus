# Worker Reconstruction Without Permanent Chats

Status: CURRENT EXODUS OPERATING CONTRACT / SOURCE-ONLY UNTIL MERGED

## Invariant

A Bus identity is a durable logical writer/routing identity, not a permanent
ChatGPT conversation, browser tab, process, endpoint, model instance, or
subjective runtime.

A future execution may occur in a temporary ChatGPT context, Work task, API
runtime, CLI process, model invocation, subagent, or other environment. That
runtime is a terminal. Destroying it must not destroy the worker.

## Where identity and authority come from

The Bus owns durable communication routing, not every worker's project role.

For a fresh runtime:

1. Resolve the logical writer and current lane from
   `architecture/contracts/RADAR_TOPOLOGY_V1.json`.
2. Read the owning project's durable role/authority contract.
   - Example: One/Two role semantics belong to BT2 source.
   - Radar's repository role belongs to `RADAR.md` and Radar authority contracts.
3. Read the current Bus protocol and writer-lane rules.
4. Read the latest applicable durable assignment/checkpoint/message.
5. Fresh-check every mutable exact subject before acting.
6. Execute only within current authority.
7. Persist results back to source PR/issue/checkpoint or Bus.

If no durable role/authority contract exists, the dispatch itself must define a
bounded role and authority. Otherwise the worker fails closed. Remembered chat
behavior is not a substitute.

## Writer lanes

A writer lane proves a durable address/provenance path only. It does not prove:
- that a worker process is currently alive;
- that a particular model/session is the worker;
- that the writer has authority over a target repository;
- that the latest message is still applicable;
- that an assigned task is complete.

`ACTIVE` in Radar topology means the lane is an active current communication
route. It does not require any permanent ChatGPT conversation to exist.

## ChatGPT Exodus interface boundary

The intended persistent ChatGPT human-interface topology is exactly:
- `Vera`
- `Vera Control Plane Coordinator`
- `BT2 Coordinator`

These are interfaces to durable state, not storage for worker identity or
project currentness. Every other worker or role is instantiated from durable
GitHub/Bus/project state as needed.

Old ChatGPT conversation/share URLs may remain in historical evidence when they
explain provenance. They must not be required to recover current state, role,
authority, assignment, or continuation.

## Slack

Slack is not a durable worker-state system or alternate Bus. Any future Slack
Vera gateway is transport/interface only; Bus/GitHub remain durable state and
protected-effect authority must remain durably recorded and verified.

## Recovery test

A worker is sufficiently dechatified when a fresh runtime with only current
project instructions/source, Bus state, durable contracts/checkpoints, and
permitted provider reads can determine:
- logical identity/role;
- authority and prohibitions;
- current assignment/frontier;
- exact evidence to refresh;
- durable communication route;
- durable output destination;
without opening an archived worker conversation.
