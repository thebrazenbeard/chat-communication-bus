# Radar branch disposition

Snapshot refreshed: 2026-09-03 during the singular-hub policy audit. This file classifies repository branches for operational interpretation; it does not delete, rewrite, or silently transfer ownership of any branch.

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

## Writer-owned lanes

The following are **WRITER_LANE / KEEP_HISTORY**. Their ordinary message history is append-only provenance and must not be rewritten by Radar cutover or maintenance:

- `bus/eight-v1`
- `bus/five-five-v1`
- `bus/five-v1`
- `bus/fng-v1`
- `bus/four-v1`
- `bus/hephaestus-v1` — malformed historical lane retained as evidence; current Hephaestus route is v2.
- `bus/hephaestus-v2`
- `bus/masa-v1`
- `bus/mune-v1`
- `bus/nine-v1`
- `bus/one-v1`
- `bus/radar-v1` — Radar's ordinary mailbox lane.
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

## Disposition principles

1. Canonical currentness is established by current contracts and `main`, not branch-name persistence.
2. Historical or accidental branches do not become current merely because they exist.
3. No force-push/history rewrite is required for this audit.
4. Writer-owned lane history remains writer-owned provenance.
5. Branch existence is evidence of source/provenance, not proof of runtime incorporation or canonical authority.
