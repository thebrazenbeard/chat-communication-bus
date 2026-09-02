# Radar branch disposition

Snapshot scope: repository branch set fresh-read on 2026-09-02 during Radar V1 integration. This file classifies branches for cutover; it does not delete, rewrite, or silently transfer ownership of any branch.

## Canonical / integration

- `main` — **HISTORICAL_STUB / CUTOVER_TARGET**. Keep unchanged until Phase 19 release/cutover verification. After cutover it should become the truthful canonical front door.
- `radar/control-plane-v1` — **CURRENT_INTEGRATION_CANDIDATE**. Radar-owned implementation branch and draft PR #2 source.

## Implementation predecessors

- `feature/slack-identity-relay-v1` — **KEEP_HISTORY / IMPLEMENTATION_PREDECESSOR**. Contains the most complete pre-Radar executable lineage: lifecycle ledger, logical identity primitives, Slack relay/idempotency behavior, tests, and CI ancestry. Radar V1 inherits useful primitives but does not treat Slack as current work-bearing coordination authority.
- `feature/chat-bus-vertical-slice-v1` — **KEEP_HISTORY / SUPERSEDED_IMPLEMENTATION_SLICE**. Earlier durable lifecycle vertical slice. Preserve for provenance; Radar V1 supersedes it as the active integration line.
- `project/vera-repo-consolidation-v1` — **KEEP_HISTORY / PROJECT_COORDINATION_LINE**. Separate historical/project coordination branch; do not merge its semantics into Radar merely because it lives in this repository.

## Protocol lineage

- `bus/protocol-v1` — **KEEP_HISTORY / SUPERSEDED_PROTOCOL**.
- `bus/protocol-v2` — **KEEP_HISTORY / CURRENT_PROTOCOL_PREDECESSOR**. Its current semantics are graduated into `docs/protocol/PROTOCOL_V2.md` on the Radar integration line. Preserve branch history rather than rewriting it.

## Writer-owned lanes

The following are **WRITER_LANE / KEEP_HISTORY**. Their ordinary message history is append-only provenance and must not be rewritten by Radar cutover:

- `bus/eight-v1`
- `bus/five-five-v1`
- `bus/five-v1`
- `bus/fng-v1`
- `bus/four-v1`
- `bus/hephaestus-v1`
- `bus/masa-v1`
- `bus/mune-v1`
- `bus/nine-v1`
- `bus/one-v1`
- `bus/seven-v1`
- `bus/six-v1`
- `bus/thirteen-v1`
- `bus/three-v1`
- `bus/two-v1`
- `bus/vera-sol-v1`
- `bus/yang-v1`
- `bus/yin-v1`

### Brigit naming lineage

- `bus/bridget-v1` — **WRITER_LANE / KEEP_HISTORY / LEGACY_SPELLING**. Logical identity is Brigit; retain the historical branch address as provenance until an explicit lane migration is performed.
- `bus/bridget-v1-tempcheck` — **KEEP_HISTORY / TEMPORARY_DIAGNOSTIC_LINE**. Do not treat this as a second Brigit identity or ordinary current writer lane.

Radar's projection layer normalizes the logical identity alias without erasing the observed branch name.

## Cutover principles

1. No historical branch deletion is required for Radar V1.
2. No force-push/history rewrite is required.
3. Writer-owned lane history remains writer-owned provenance.
4. Branch existence is evidence of source/provenance, not proof of runtime incorporation.
5. After Phase 19 cutover, successor/current pointers should make historical branches easy to recognize without requiring deletion.
