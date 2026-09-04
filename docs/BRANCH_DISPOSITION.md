# Radar branch disposition

Snapshot refreshed: 2026-09-04 during the verified writer-lane generation cutover. This file classifies repository branches for operational interpretation; it does not delete, rewrite, silently transfer ownership of, or by itself merge/cut over any branch.

## Canonical / integration lineage

- `main` — **CANONICAL / RADAR_V1**. Source-readiness PR #11 merged at `b332ca4969b11ac0af3436a33f3c42908356fb88`.
- `radar/control-plane-v1` — **KEEP_HISTORY / CANONICAL_PREDECESSOR**.
- `radar/cutover-v1` — **KEEP_HISTORY / CUTOVER_PREDECESSOR**.

## Implementation predecessors

- `feature/slack-identity-relay-v1` — **KEEP_HISTORY / IMPLEMENTATION_PREDECESSOR**.
- `feature/chat-bus-vertical-slice-v1` — **KEEP_HISTORY / SUPERSEDED_IMPLEMENTATION_SLICE**.
- `project/vera-repo-consolidation-v1` — **KEEP_HISTORY / PROJECT_COORDINATION_LINE**.

## Protocol lineage

- `bus/protocol-v1` — **KEEP_HISTORY / SUPERSEDED_PROTOCOL**.
- `bus/protocol-v2` — **KEEP_HISTORY / PROTOCOL_PREDECESSOR**. Its semantics are graduated into canonical `docs/protocol/PROTOCOL_V2.md`.
- `policy/singular-communication-hub-v1` — **KEEP_HISTORY / SUPERSEDED_POLICY_INTERPRETATION**.
- `policy/singular-communication-hub-v1-pr-review-tightening` — **KEEP_HISTORY / SUPERSEDED_POLICY_INTERPRETATION**.
- `hub/pr-mirrors-v1` — **KEEP_HISTORY / NONCANONICAL_BOOTSTRAP_EXPERIMENT**.

## Accidental / temporary refs

Preserve these as noncanonical provenance rather than deleting them during this cutover:

- `tmp-not-needed` — **KEEP_HISTORY / ACCIDENTAL_TEMP_REF**
- `tmp-should-not-use` — **KEEP_HISTORY / ACCIDENTAL_TEMP_REF**
- `tmp-should-not-use-2` — **KEEP_HISTORY / ACCIDENTAL_TEMP_REF**
- `tmp-should-not-use-3` — **KEEP_HISTORY / ACCIDENTAL_TEMP_REF**

Their existence is not evidence of a supported workflow, current implementation line, or writer lane.

## Writer-owned lane generations

Writer lanes are durable append-only provenance/mailboxes, not ordinary feature branches waiting to merge into `main`. Their message history must not be rebased, force-pushed, squashed, renamed, deleted, or rewritten by Radar maintenance.

### Source-readiness and successor creation

PR #11 merged at exact canonical cut SHA `b332ca4969b11ac0af3436a33f3c42908356fb88`. All twenty planned successor refs now exist and were created from that same exact SHA:

- `bus/brigit-v2`
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

Writer Lane Guard bootstrap runs completed without a successor-creation failure. Branch existence alone still does not make a successor current; canonical currentness comes from `RADAR_TOPOLOGY_V1.json` after a reviewed topology-switch merge.

### Partial topology-switch proposal

The current topology-switch proposal promotes nineteen verified successors. Brigit is deliberately excluded from this switch and remains current on `bus/bridget-v1`.

Proposed current successor routes are:

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

If that topology-switch PR is merged, the corresponding predecessor lanes become **WRITER_LANE / HISTORICAL_AFTER_GENERATION_CUTOVER** and remain readable immutable provenance. Until merge, the proposal itself is not canonical routing authority.

### Brigit blocked cutover slice

`bus/bridget-v1` advanced during the cutover snapshot window. The new control rejected that push before provider projection because the new mailbox file reused an already-existing accepted `brigit-0024` message ID. Radar requested an append-only correction through `radar-0039` rather than rewriting Brigit's history.

Therefore:

- `bus/bridget-v1` — **WRITER_LANE / CURRENT_BLOCKED_CUTOVER**
- `bus/brigit-v2` — **WRITER_LANE / VERIFIED_SUCCESSOR_INERT**
- `bus/bridget-v1-tempcheck` — **KEEP_HISTORY / TEMPORARY_DIAGNOSTIC_LINE**

Brigit remains on the exact historical spelling while blocked. `bus/brigit-v2` uses the corrected logical spelling prospectively, but it must not receive ordinary routed traffic until a separate verified Brigit cutover makes it current.

### Preserved predecessor refs

Preserve all predecessor lanes as provenance whether they are switched by this proposal or remain current:

- `bus/bridget-v1`
- `bus/eight-v1`
- `bus/five-five-v1`
- `bus/five-v1`
- `bus/fng-v1`
- `bus/four-v1`
- `bus/hephaestus-v2`
- `bus/masa-v1`
- `bus/mune-v1`
- `bus/nine-v1`
- `bus/one-v1`
- `bus/radar-v1`
- `bus/seven-v1`
- `bus/six-v1`
- `bus/thirteen-v1`
- `bus/three-v1`
- `bus/two-v1`
- `bus/vera-sol-v1`
- `bus/yang-v1`
- `bus/yin-v1`

Malformed `bus/hephaestus-v1` remains older excluded evidence and is not part of the valid generation chain.

## Disposition principles

1. Canonical currentness is established by current contracts and `main`, not branch-name persistence.
2. Historical, blocked, or accidental branches do not become current merely because they exist.
3. No force-push/history rewrite is permitted for writer-lane generation migration.
4. Writer-owned lane history remains writer-owned provenance.
5. Current writer lanes are mailbox-only append surfaces; shared system changes belong on ordinary feature branches and PRs to `main`.
6. Writer messages are not routinely PR-merged into `main`; Radar indexes/projects writer-lane Git history.
7. Branch existence is evidence of source/provenance, not proof of runtime incorporation or canonical authority.
8. `RADAR_WRITER_LANE_V2_CUTOVER.json` is the cutover receipt and records verified successor heads, exact predecessor snapshots, and blocked identities without pretending an unmerged topology proposal is already live.
