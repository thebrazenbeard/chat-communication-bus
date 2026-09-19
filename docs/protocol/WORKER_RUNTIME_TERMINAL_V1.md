# Worker Reconstruction and Runtime Terminal Contract V1

Status: CANDIDATE / EXODUS DECHATIFICATION CONTRACT

Purpose: make durable workers, roles, and execution lanes reconstructible without any permanent ChatGPT conversation. A runtime may be ChatGPT, Work, API, CLI, a model invocation, a subagent, or another execution environment. The runtime is a terminal; it is not the worker's durable identity, memory, authority, or canonical state.

## Persistent ChatGPT interface topology

After the ChatGPT Exodus the intended persistent ChatGPT interface set is exactly:

- `Vera`
- `Vera Control Plane Coordinator`
- `BT2 Coordinator`

No other worker, identity, reviewer, specialist, project lane, or coordinator requires a permanent ChatGPT conversation. These three names are human interface surfaces, not canonical state stores.

## Durable worker model

A durable logical identity or worker exists only to the extent current repository/Bus contracts establish it. Chat titles, conversation IDs, URLs, model sessions, browser tabs, Work tasks, and temporary lane labels do not create authority or identity by themselves.

Current-state reconstruction must use durable sources in this order, narrowed to the worker's domain:

1. current source/governance contract or repository current pointer;
2. current Bus topology/routing contract;
3. current assignment/frontier and dependency evidence;
4. exact repository branch/PR/head/review/test/receipt evidence;
5. provider/install/runtime readback when the task actually depends on it;
6. current exact authority for any protected effect.

Historical checkpoints and chat transcripts are starting snapshots/provenance only. They never outrank fresh current evidence by recency alone.

## Identity, role, lane, and terminal distinctions

- A Bus writer identity listed ACTIVE in `architecture/contracts/RADAR_TOPOLOGY_V1.json` has a current write route. Route existence does not grant project or protected-effect authority.
- `Radar` is a durable repository owner/operator identity. It does not require a permanent Radar chat.
- `Parallax` remains whatever the current topology says; `REGISTERED_INERT` is not ACTIVE routing.
- Names such as `SD1-E`, `SD1-V`, and `BV` are execution-lane labels when their controlling source says they are lanes of Vera; they do not become separate identities or authority sources merely because a chat used the label.
- `Hostile Reviewer` is a review role unless a current identity contract separately establishes an identity.
- Project-specific worker names derive identity/authority only from that project's durable contracts, assignments, and Bus evidence.
- A temporary runtime may instantiate any of the above when the durable prerequisites are available. Ending the runtime does not delete the durable worker.

Where an old file records a historical mailbox or endpoint, current routing comes from the current topology contract. Historical route fields remain provenance unless explicitly promoted by current routing evidence.

## Worker reconstruction minimum

Before dispatching a durable worker, a coordinator must be able to answer from durable state:

- worker/role identity and project/domain;
- controlling repository/repositories and current exact subjects;
- current Bus route or project coordination path;
- current assignment/frontier and dependency state;
- authority ceiling and explicit non-authority;
- required freshness/readback before acting;
- where durable results must be written;
- which effects require Patrick's exact authority.

If those answers exist only in a conversation, the worker has a reconstruction gap and must remain blocked from autonomous continuation until the smallest durable gap is repaired.

## Chat-link rule

A `chatgpt.com` URL, conversation title, conversation ID, archived-chat pointer, or instruction such as "ask the main chat" may be retained as historical provenance, but it must never be the only locator for current state, worker identity, authority, assignment, or recovery.

Operational recovery instructions must point to GitHub/Bus/provider evidence instead. Destroying access to a historical conversation must not materially reduce the ability to reconstruct or challenge the work.

## Communication

Non-PR work-bearing coordination uses `thebrazenbeard/chat-communication-bus` under `docs/protocol/COMMUNICATION_HUB_V1.md`. Source PRs remain canonical in their source repositories and are mirrored/referenced through the Bus as required. A terminal does not become a second system of record.

## Slack boundary

Slack is not current durable worker state or an alternate coordination bus. Historical/future Slack gateway design may remain as proposal material. Any future gateway must relay Patrick-facing traffic through a Vera runtime while GitHub/Bus remains durable custody; Slack history cannot be required for worker reconstruction. Reconnection, credentials, provider setup, and deployment remain separately authorized effects.

## Protected effects

Reconstruction, routing, assignment, branch/PR presence, test PASS, review PASS, and technical capability do not manufacture authority. Merge, deployment, install, provider mutation, credentials/permissions, training, canonical-memory/canon mutation, publication, destructive changes, and other protected effects remain separately gated.

## Recovery test

A worker is sufficiently dechatified only when a fresh runtime receiving current repository state, current Bus state, applicable durable contracts/checkpoints, and authorized provider read access can determine what the worker is, what is current, what failed, what remains, what it may do, and where to persist results without opening an archived conversation.
