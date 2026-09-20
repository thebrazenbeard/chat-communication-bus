# Worker Runtime Reconstruction V1

Status: EXODUS CANDIDATE / REVIEW REQUIRED

A worker is reconstructed from durable state. A conversation is only one possible execution terminal.

## Permanent human interfaces

The intended persistent ChatGPT interface topology is exactly:

- Vera
- Vera Control Plane Coordinator
- BT2 Coordinator

No other worker requires a permanent ChatGPT conversation.

Persistent human interfaces resolve their own non-PR coordination semantics through
`architecture/contracts/PERSISTENT_INTERFACE_ROUTING_V1.json`. Interface routing and
worker routing are intentionally distinct: a persistent interface does not become a
`RADAR_TOPOLOGY_V1.json` writer identity merely because it coordinates work.

## Runtime-neutral reconstruction

Before an ephemeral runtime acts as Radar, One, Two, Three, Four, Noah, Parallax, Hephaestus, a project worker, a hostile reviewer, or a future worker, it must reconstruct from durable evidence:

1. the target project's current governance/currentness source;
2. the current Bus topology when Bus routing is relevant;
3. the current durable assignment/frontier;
4. the worker/project role contract where one exists;
5. fresh exact-head review/provider/effect evidence needed for the task;
6. current authority boundaries.

The runtime then receives only the authority supported by that evidence.

A browser tab, chat URL, conversation title, model label, remembered prompt, or old assignment cannot fill a missing durable field.

## Identity classes

Bus writer identities are routing/provenance identities. Topology registration alone does not give a standing project role or effect authority. Their current work comes from durable assignment/project state.

Project identities such as Radar and Noah are reconstructed from their owning repository contracts.

Labels such as SD1-E, SD1-V, BV, and VW are execution-lane labels, not independent durable identities. Their useful state belongs to the owning project repositories and Bus evidence.

A reviewer is normally assignment-scoped. A hostile-review runtime may be instantiated fresh, produce an exact-subject review receipt, and disappear without losing the review.

## Communication

Worker identities use the current Bus route from the canonical topology. Persistent human interfaces resolve interface-specific coordination semantics through `PERSISTENT_INTERFACE_ROUTING_V1.json`; an interface coordination branch is not thereby promoted into the worker topology.

Source PRs remain canonical in their source repositories and are referenced through the Bus when appropriate.

Never hard-code a historical worker branch as current routing authority. Historical lanes remain provenance. Interface-route bindings must themselves be current, explicit, and separately governed.

## Recovery failure

If current project role, assignment, routing, source, or authority cannot be reconstructed:

- preserve the ambiguity;
- do not infer from an archived chat;
- do not create a replacement permanent chat;
- mark the worker/task WAITING or WORKER_RECONSTRUCTION_GAP;
- continue other independent safe work.

## Slack

Slack is not activated by this contract. A future Slack gateway may expose Vera to Patrick, but Bus/GitHub remain durable state and coordination infrastructure. Slack history must not become necessary for worker reconstruction.

This contract grants no merge, deployment, provider, credential, permission, spend, publication, training, or other protected-effect authority.
