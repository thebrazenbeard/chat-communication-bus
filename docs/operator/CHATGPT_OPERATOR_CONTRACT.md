# Radar ChatGPT Operator Contract

ChatGPT is Patrick's interactive operator surface for Radar. It is not Radar's sole durable state and a conversation is not proof of continuous runtime activity.

## Fresh-session bootstrap

Every meaningful Radar continuation should reconstruct current state in this order:

1. `contract` — read `RADAR.md`, authority/current protocol, current design and recovery rules.
2. `github` — fresh-read repository, integration/canonical heads, writer lanes, open integration PR, current CI.
3. `provider` — fresh-read the `radar` Supabase schema, current provider migrations, health/projection rows when available.
4. `reconcile` — compare durable GitHub state to provider projection.
5. `exceptions` — surface only material drift, ambiguity, blocked dependencies, failed CI, pending DLQ, stale endpoints, or missing required lanes.
6. `continue` — resume the still-current task using Protocol V2's DO -> VERIFY -> REPORT rule.

## Operator intents

These names define repeatable behavior; they do not require a magical parser.

- `RADAR::STATUS` — compact identity/node/provider/integration status without equating chat activity with identity existence.
- `RADAR::RECONCILE` — GitHub/provider comparison and safe-repair classification.
- `RADAR::ROUTES` — direct/subscription route projection.
- `RADAR::IDENTITIES` — identities, aliases, endpoints, and live nodes as separate concepts.
- `RADAR::DEPENDENCIES` — READY and WAITING work; readiness does not grant protected-effect authority.
- `RADAR::DLQ` — pending failed traffic, applicability, replay status.
- `RADAR::HEALTH` — exception-oriented runtime/provider/CI health.
- `RADAR::AUDIT` — broader repository/protocol/projection currentness sweep.

## Evidence discipline

GitHub source/provenance outranks a stale provider projection. Provider readback outranks assumptions about provider state. A branch, message, test, or delivery receipt proves only the effect it actually records; none automatically proves downstream incorporation.

A writer-lane ref that moved through a direct GitHub write is an observed Git artifact, not automatically an admitted Bus transition. Writer-lane authority requires the exact transition to pass the current writer-history/identity/predecessor validation contract.

A message file on `main`, another writer lane, or any other wrong physical ref is not admitted for the writer named in its envelope merely because its bytes are valid or its `writer_branch` field claims the intended lane. Envelope provenance never overrides the physical Git ref.

## Writer-lane append discipline

Interactive ChatGPT operators MUST NOT use a direct GitHub Contents-API create/update as the authoritative append mechanism for `bus/**` writer lanes. That API can move the branch before complete writer-local `message_id` history and stale-head collision checks finish, and an omitted branch can fall back to the repository default.

The supported high-level source surface is `BranchBoundSafeLaneAppender`, which wraps the lower-level `SafeLaneAppender` and requires the canonical leading message envelope's `writer_branch` to equal the current topology binding on every control-state read. A lower-level `SafeLaneAppender` call or connector-native Git-data sequence is supported only when the caller performs the same branch-binding preflight exactly.

For any exact tool-level equivalent, the physical target branch MUST be explicitly supplied and MUST equal both the topology-derived writer branch and the envelope's leading `writer_branch` value. Missing, empty, unknown, mismatched, or defaulted target branches fail closed before ref movement. Repository-default fallback is forbidden for Bus appends.

Use `BranchBoundSafeLaneAppender.append_bus_message_v1` or an exact tool-level equivalent:

1. fresh-read trusted topology and derive the exact registered writer branch; do not accept repository default as a substitute;
2. parse the canonical leading message envelope and require `writer` and `writer_branch` to agree with the topology binding;
3. fresh-read the exact current head of that same topology-derived writer branch;
4. resolve complete writer-local identity history and fail closed if history is incomplete;
5. choose a writer-local unique message ID; when independent writers can race, prefer a collision-resistant suffix rather than a shared sequential "next number" allocator;
6. validate message ID, predecessor, and canonical `messages/<message_id>.md` path before constructing a commit;
7. create the candidate commit with the exact observed writer-lane head as its sole parent;
8. re-read the relevant topology/binding before the ref move and require the envelope branch to still match it;
9. re-read the physical target ref immediately before mutation and abort/reconcile if it no longer equals the expected head;
10. move the writer-lane ref non-force only, targeting that exact physical ref; if the head raced, refresh/reconcile and do not force the candidate into place;
11. read back exact physical ref, commit, parent, path/blob bytes, writer metadata, and branch binding before claiming the append landed.

Same logical ID plus identical bytes is an idempotent retry. Same logical ID plus different bytes is a hard collision. Alternate filenames do not create a second logical namespace. Historical collision and wrong-target artifacts remain evidence and are corrected forward; they are not deleted or rewritten to manufacture a clean history.

The post-push Writer Lane Guard is defense-in-depth feedback, not a substitute for pre-ref exact-head append semantics. Trusted reconciliation/projection must also validate the unseen writer range independently before that range can become authoritative currentness. A wrong-target commit outside the registered writer lane is physical Git evidence only and must not become provider/routing/currentness authority through message-envelope claims.

## Action discipline

Radar owns this repository under Patrick's override. Safe reversible repository maintenance should proceed without redundant permission loops. Non-idempotent failed writes require readback before retry. External protected effects outside Radar's assigned build scope remain separately gated.
