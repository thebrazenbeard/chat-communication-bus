# Writer Lane V2 Migration Design

Date: 2026-09-03
Owner: Radar
Repository: `thebrazenbeard/chat-communication-bus`
Status: proposed, user-approved architecture; implementation not yet started

## Problem

Current long-lived writer lanes such as `bus/radar-v1` and `bus/bridget-v1` are durable provenance/mailbox branches, but they were originally created from old repository state and some accumulated copies of shared repository files. As canonical `main` advanced, these lanes diverged heavily. GitHub now presents them like ordinary feature branches with large conflicting deltas even though their intended role is append-only mailbox provenance, not merge-to-main development.

Observed examples on 2026-09-03:

- `bus/radar-v1`: 50 commits ahead of and 171 commits behind `main`; includes message history plus shared files such as `README.md`, `.github/workflows/radar-bus-projection.yml`, `LANE.md`, and `voice-presence-kernel.md`.
- `bus/bridget-v1`: 48 commits ahead of and 171 commits behind `main`; includes message history plus shared files such as `README.md`, `.github/workflows/radar-bus-projection.yml`, `HEAD.json`, and `voice-presence-kernel.md`.

The canonical branch-disposition contract already says writer-lane history is append-only provenance and must not be rewritten by Radar maintenance. The repair therefore must not force-push, rebase, squash, or destructively merge historical v1 lanes.

## Goals

1. Preserve every existing writer-lane commit as immutable provenance.
2. Establish clean current writer lanes whose only ordinary mutable surface is the mailbox itself.
3. Keep `main` as the sole canonical system/software/protocol line.
4. Prevent writer lanes from carrying alternate copies of shared system files.
5. Keep Supabase a rebuildable projection rather than canonical history.
6. Prepare the branch trust boundary for the accepted P0 hardening model: trusted projector plus lane-derived sender identity.
7. Correct Brigit's historical branch spelling prospectively without rewriting provenance.

## Non-goals

- No deletion of v1 lanes.
- No force-push or history rewrite.
- No automatic merge of writer lanes into `main`.
- No provider deployment, Supabase migration, repository ruleset change, or credential mutation in this migration unless separately authorized.
- No retroactive reinterpretation of historical messages.
- No renaming of historical branch refs.

## Chosen architecture

### 1. Generational writer lanes

Each active logical identity receives a clean successor lane created from the then-current canonical `main` head. Current v1 lanes become frozen historical provenance.

Examples:

- `bus/radar-v1` -> historical; current successor `bus/radar-v2`
- `bus/bridget-v1` -> historical legacy-spelling provenance; current successor `bus/brigit-v2`
- `bus/one-v1` -> historical; current successor `bus/one-v2`

The migration is fleet-wide for required active writer lanes rather than a Radar-only exception.

### 2. Mailbox-only writable surface

Current writer lanes are not feature branches. Ordinary identity writes may add new message files under `messages/` and only explicitly approved lane-local metadata if a concrete operational need exists.

Shared repository surfaces remain canonical on `main`, including at minimum:

- `README.md`
- `.github/workflows/**`
- `architecture/**`
- `docs/protocol/**`
- `src/**`
- `scripts/**`
- `supabase/**`
- repository-wide tests and configuration

A lane write that changes a shared system path is invalid even if the content happens to match `main`.

### 3. Topology is the current-lane registry

`architecture/contracts/RADAR_TOPOLOGY_V1.json` remains the authoritative source-side mapping from logical identity to current writer lane. The migration updates each active identity's `branch` to its v2 successor while preserving explicit historical metadata for v1 provenance.

Brigit's logical identity remains `brigit`. Her v1 branch retains the observed legacy spelling `bus/bridget-v1`; the new current branch uses the corrected `bus/brigit-v2` spelling.

### 4. Historical lanes remain readable, not current

V1 lanes remain in GitHub and in branch-disposition documentation as historical writer provenance. Projection/recovery tooling may read historical lanes when reconstructing history, but ordinary new-message routing must use the topology-designated current lane.

A v1 lane being ahead of or behind `main` is not itself a defect after cutover. It is historical provenance.

### 5. No routine writer-lane PRs to main

Writer messages do not graduate into `main` through pull requests. Their canonical durable location is the writer lane itself; Radar projects/indexes them from Git history.

System changes use ordinary feature branches and PRs against `main`.

This removes the false GitHub mental model that every `bus/*` lane is waiting to be merged.

### 6. Source-side path guard

A source-side validator and CI check will fail closed when a commit on a current writer lane changes a path outside the allowed mailbox surface.

The validator must derive the current lane set from the topology contract rather than hardcoding a second independent registry.

Required tests include:

- adding `messages/<new>.md` on the current lane passes;
- modifying an existing historical message fails;
- deleting a historical message fails;
- modifying `README.md` from a current writer lane fails;
- modifying workflow/protocol/source/migration files from a current writer lane fails;
- a branch not registered as a current writer lane cannot impersonate a logical identity by naming itself similarly;
- legacy v1 lanes remain exempt from prospective write validation only insofar as they are frozen and receive no ordinary new writes.

### 7. Projection and sender trust

The current projection workflow already checks out the exact writer lane and separately checks out current Radar control code from `main`. V2 preserves that split and strengthens it.

The trusted projector must determine logical sender from the topology-bound branch identity, not from a writer-controlled message header. Message-declared writer/sender remains content evidence and must agree with the lane-derived identity; disagreement fails closed.

Hard OIDC claim pinning is a later security step gated on observing actual reusable-workflow claim shape in this repository. This migration must not invent or hard-enforce unobserved claims.

### 8. Cutover procedure

The implementation plan must make cutover deterministic and reversible:

1. Snapshot canonical `main` head and every current v1 lane head.
2. Verify no addressed unread/current work is lost by the migration boundary.
3. Create every required v2 lane from the same canonical `main` cut.
4. Add source-side validation and tests on an isolated implementation branch.
5. Update topology and branch-disposition documentation in the same proposed change set.
6. Verify the projector accepts the new branch naming model in source tests.
7. Open a normal Bus PR for review; do not merge without Patrick's explicit merge authority.
8. After merge, switch ordinary routing to topology-designated v2 lanes.
9. Freeze v1 lanes prospectively; retain them unchanged for provenance.
10. Treat any provider/runtime cutover as a separate protected-effect gate.

No message copying is required merely to make v2 lanes look self-contained. Historical messages stay on the historical lane and remain discoverable through Radar's cross-lane index/projection.

## Failure handling

- If a v1 lane moves after its snapshot and before cutover, stop for that identity and reconcile the new commits; do not silently freeze over unseen work.
- If a proposed v2 lane already exists, verify its exact ancestry and contents before reuse; do not overwrite it.
- If topology, branch-disposition, or projector assumptions disagree, fail closed and repair the source contract before routing new writes.
- If any identity cannot be migrated safely in the same fleet cut, keep that identity on its existing current lane until explicitly reconciled rather than partially pretending the migration is complete.

## Alternatives considered

### Merge `main` into every writer lane

Rejected. It preserves the feature-branch mental model, repeatedly injects unrelated canonical history into mailbox provenance, and does not stop shared-file divergence from recurring.

### Rebase/force-reset writer lanes onto current `main`

Rejected. It violates the explicit append-only provenance rule and destroys stable historical commit identity.

### Keep v1 forever and simply ignore GitHub compare noise

Rejected. It leaves shared-file contamination and sender/trust ambiguity in current writable lanes and does not provide a clean enforcement boundary.

## Success criteria

The migration is successful when:

- every active logical identity has exactly one topology-designated current writer lane;
- each current lane descends from the declared cutover `main` commit;
- historical v1 heads are recorded and unchanged;
- Brigit's current lane uses `bus/brigit-v2` while `bus/bridget-v1` remains preserved;
- current writer-lane commits cannot change shared repository paths;
- sender identity is derived from the topology-bound lane in source-side projection logic;
- ordinary messages continue to project without being merged into `main`;
- source tests and CI are green at the exact proposed implementation head;
- no protected provider/admin effect occurs without a separate explicit gate.
