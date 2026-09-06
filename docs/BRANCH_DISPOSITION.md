# Radar branch disposition

Currentness refresh: 2026-09-06. This document classifies branches for operational interpretation. It does not delete, rewrite, merge, activate, or transfer ownership of any branch.

## Canonical and source branches

- `main` — **CANONICAL GITHUB SOURCE LINE**.
- `radar/control-plane-v1` — **KEEP_HISTORY / HISTORICAL_CANONICAL_PREDECESSOR**.
- `radar/cutover-v1` — **KEEP_HISTORY / HISTORICAL_CUTOVER_PREDECESSOR**.
- current `radar/**` hardening branches and their Draft PRs — **SOURCE_WORKSTREAM / NOT CURRENT UNTIL MERGED**. Branch existence or a Draft PR does not imply provider deployment, workflow activation, or runtime qualification.

## Current writer lanes

Canonical routing currentness comes only from `architecture/contracts/RADAR_TOPOLOGY_V1.json`, not from branch names or this summary.

Lifecycle `ACTIVE` current lanes at this refresh are:

- `bus/bridget-v1` — Brigit explicit legacy-spelling exception.
- `bus/eight-v2`
- `bus/five-five-v2`
- `bus/five-v2`
- `bus/fng-v2`
- `bus/four-v2`
- `bus/hephaestus-v3`
- `bus/masa-v2`
- `bus/mune-v2`
- `bus/nine-v2`
- `bus/one-v2`
- `bus/radar-v2`
- `bus/seven-v2`
- `bus/six-v2`
- `bus/thirteen-v2`
- `bus/three-v2`
- `bus/two-v2`
- `bus/vera-v2`
- `bus/yang-v2`
- `bus/yin-v2`

`bus/parallax-v1` is **REGISTERED_INERT / FIRST_APPEND_PENDING**. Its topology registration merged, but it is not routing/reconciliation authority until its first append passes the current Writer Lane Guard and a subsequent currentness change marks it ACTIVE.

`bus/brigit-v2` remains inert/noncurrent while Brigit uses `bus/bridget-v1`.

## Historical writer lanes

All predecessor writer lanes remain immutable provenance. This includes `bus/radar-v1`, `bus/vera-sol-v1`, the v1 predecessors of current v2 lanes, `bus/hephaestus-v2`, and other predecessor refs recorded in `architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json`.

That cutover file is a dated historical receipt. It is not a current routing map and must not be replayed as current topology during recovery.

Malformed/diagnostic refs such as `bus/hephaestus-v1` and `bus/bridget-v1-tempcheck` remain noncanonical evidence only.

## Protocol and implementation predecessors

Historical feature/protocol/policy branches remain KEEP_HISTORY provenance unless a current contract says otherwise. Examples include:

- `feature/slack-identity-relay-v1`
- `feature/chat-bus-vertical-slice-v1`
- `bus/protocol-v1`
- `bus/protocol-v2`
- prior policy/hub experiment branches

Their existence is not evidence that the corresponding transport/protocol implementation is active today.

## Disposition principles

1. `main` plus current contracts establish source/currentness; branch persistence does not.
2. Only topology lifecycle `ACTIVE` writer lanes are current routing/reconciliation authority.
3. Writer lanes are mailbox/provenance surfaces, not ordinary branches to merge into `main`.
4. Writer history must not be rebased, force-pushed, squashed, renamed, deleted, or rewritten by Radar maintenance.
5. Shared system changes belong on ordinary source branches/PRs, never by modifying writer-lane history.
6. Historical cutover/onboarding evidence does not become present topology merely because it remains readable.
7. Provider state, workflow activation, and behavioral qualification are separate axes from source merge/currentness.
8. Protected effects remain Patrick-gated regardless of branch/PR status.
