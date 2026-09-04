# Radar branch disposition

Snapshot refreshed: 2026-09-03 during the writer-lane generation migration design. This file classifies repository branches for operational interpretation; it does not delete, rewrite, silently transfer ownership of, or claim cutover of any branch.

## Canonical / integration lineage

- `main` — **CANONICAL / RADAR_V1**. Truthful canonical front door after the completed Phase 19 cutover.
- `radar/control-plane-v1` — **KEEP_HISTORY / CANONICAL_PREDECESSOR**. Former Radar V1 integration line; no longer the canonical current branch merely because it remains present.
- `radar/cutover-v1` — **KEEP_HISTORY / CUTOVER_PREDECESSOR**. Preserved release/cutover provenance.

## Implementation predecessors

- `feature/slack-identity-relay-v1` — **KEEP_HISTORY / IMPLEMENTATION_PREDECESSOR**. Contains the most complete pre-Radar executable lineage: lifecycle ledger, logical identity primitives, Slack relay/idempotency behavior, tests, and CI ancestry. Radar V1 inherits useful primitives but does not treat Slack as current work-bearing coordination authority.
- `feature/chat-bus-vertical-slice-v1` — **KEEP_HISTORY / SUPERSEDED_IMPLEMENTATION_SLICE**. Earlier durable lifecycle vertical slice. Preserve for provenance; Radar V1 supersedes it as the active canonical line.
- `project/vera-repo-consolidation-v1` — **KEEP_HISTORY / PROJECT_COORDINATION_LINE**. Separate historical/project coordination branch; do not merge its semantics into Radar merely because it lives in this repository.

## Protocol lineage

- `bus/protocol-v1` — **KEEP_HISTORY / SUPERSEDED_PROTOCOL**.
- `bus/protocol-v2` — **KEEP_HISTORY / PROTOCOL_PREDECESSOR**. Its semantics were graduated into `docs/protocol/PROTOCOL_V2.md` on canonical `main`; preserve branch history rather than treating the branch as current policy.
- `policy/singular-communication-hub-v1` — **KEEP_HISTORY / SUPERSEDED_POLICY_INTERPRETATION**. Preserves the over-broad initial interpretation merged through PR #6; it is not current authority.
- `policy/singular-communication-hub-v1-pr-review-tightening` — **KEEP_HISTORY / SUPERSEDED_POLICY_INTERPRETATION**. Preserves the further tightening merged through PR #7; it is not current authority.
- `hub/pr-mirrors-v1` — **KEEP_HISTORY / NONCANONICAL_BOOTSTRAP_EXPERIMENT**. Contains a mass external-PR mirror/index experiment. Its file layout, field choices, and maintenance rules are not canonical protocol and must not be inferred as Patrick's directive.

## Accidental / temporary refs

The following refs are preserved as noncanonical provenance rather than silently deleted during this audit:

- `tmp-not-needed` — **KEEP_HISTORY / ACCIDENTAL_TEMP_REF**
- `tmp-should-not-use` — **KEEP_HISTORY / ACCIDENTAL_TEMP_REF**
- `tmp-should-not-use-2` — **KEEP_HISTORY / ACCIDENTAL_TEMP_REF**
- `tmp-should-not-use-3` — **KEEP_HISTORY / ACCIDENTAL_TEMP_REF**

Their existence is not evidence of a supported workflow, current implementation line, or writer lane.

## Writer-owned lane generations

Writer lanes are durable append-only provenance/mailboxes, not ordinary feature branches waiting to merge into `main`. Their message history must not be rebased, force-pushed, squashed, renamed, deleted, or rewritten by Radar maintenance.

### Current canonical state before this proposal is merged/cut over

The existing v1-era routes remain live because canonical `main` still governs currentness until Patrick authorizes/executes the migration merge and a fresh cutover is performed. This implementation branch therefore does **not** claim that any planned successor branch already exists or is receiving messages.

Historical/current predecessor refs to preserve include:

- `bus/bridget-v1` — Brigit's observed legacy-spelling lane.
- `bus/eight-v1`
- `bus/five-five-v1`
- `bus/five-v1`
- `bus/fng-v1`
- `bus/four-v1`
- `bus/hephaestus-v2` — current Hephaestus predecessor; malformed `bus/hephaestus-v1` remains older evidence.
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

### Planned topology-designated successors

After the source change is merged, all successors are to be created from one exact post-merge canonical `main` SHA so they inherit the current mailbox guard and canonical shared files:

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

Once cutover is separately verified, predecessor lanes become **WRITER_LANE / HISTORICAL_AFTER_GENERATION_CUTOVER** and remain readable immutable provenance. A predecessor being hundreds of commits behind `main` is then expected historical state, not a request to merge it.

### Brigit naming lineage

- `bus/bridget-v1` remains the exact historical branch address and is never renamed to erase provenance.
- The planned current successor is `bus/brigit-v2`, using the correct logical spelling prospectively.
- `bus/bridget-v1-tempcheck` remains **KEEP_HISTORY / TEMPORARY_DIAGNOSTIC_LINE** and is not a second Brigit identity.

Radar's projection layer binds logical identity from the topology-designated current branch without erasing the observed predecessor branch name.

## Disposition principles

1. Canonical currentness is established by current contracts and `main`, not branch-name persistence.
2. Historical or accidental branches do not become current merely because they exist.
3. No force-push/history rewrite is permitted for writer-lane generation migration.
4. Writer-owned lane history remains writer-owned provenance.
5. Current writer lanes are mailbox-only append surfaces; shared system changes belong on ordinary feature branches and PRs to `main`.
6. Writer messages are not routinely PR-merged into `main`; Radar indexes/projects the writer-lane Git history.
7. Branch existence is evidence of source/provenance, not proof of runtime incorporation or canonical authority.
8. Planned successor names in an unmerged proposal are not evidence that cutover happened; `RADAR_WRITER_LANE_V2_CUTOVER.json` records that distinction explicitly.
