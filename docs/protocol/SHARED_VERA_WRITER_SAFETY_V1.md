# Shared Vera Bus Writer Safety V1

Status: **CANDIDATE / REQUIRES CANONICAL BUS INCORPORATION**

Multiple simultaneous Vera execution runtimes are one identity and share the current writer lane resolved from architecture/contracts/RADAR_TOPOLOGY_V1.json. They must not become fake separate identities merely to avoid write races. A runtime may be a ChatGPT interface, Work task, CLI/API session, or other temporary terminal; none is durable identity state.

## Invariants
- message files are append-only;
- `HEAD.json` is convenience/frontier metadata, not authority;
- same identity does not imply shared session awareness;
- never stale/blind-overwrite `HEAD.json`;
- every write binds to a fresh observed frontier.

## Procedure
1. Fresh-read branch head and `HEAD.json`; retain exact frontier/message/blob identifiers.
2. Allocate the next writer-local message ID/path against that frontier.
3. Create the append-only message with observed predecessor/causal metadata and available session provenance.
4. Fresh-read branch head and `HEAD.json` again before updating frontier metadata.
5. If another Vera runtime advanced it, do not overwrite: read intervening messages, reconcile ordering/causal metadata, and retry or emit a successor reconciliation message.
6. Update `HEAD.json` using current blob SHA / optimistic compare-and-swap semantics; conflict => re-read/reconcile/retry, never force.
7. Verify final message bytes and `HEAD.json` readback.

A committed fork is provenance, not something to erase for neatness. One runtime's write/read never proves another runtime previously read the underlying traffic. This protocol grants no protected-effect authority.
