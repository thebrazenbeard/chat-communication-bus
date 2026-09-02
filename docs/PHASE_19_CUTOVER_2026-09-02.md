# Radar Phase 19 canonical cutover receipt — 2026-09-02

## Decision and source

Patrick authorized Phase 19 canonical cutover with `Fire when ready` after Radar had reported Phase 19 readiness.

- Repository: `thebrazenbeard/chat-communication-bus`
- Canonical target: `main`
- Verified source branch: `radar/control-plane-v1`
- Verified source head: `e52639a25ce9b5f68831659c3c3500ba0384124c`
- Original integration PR: #2 (draft evidence surface)
- Cutover PR: #3
- Canonical merge commit: `1b47b32b9d5a4badd2af5e9943be75be61e1c143`

The cutover used a separate non-draft branch `radar/cutover-v1` pointing at the exact verified source head because the available ready-for-review connector mutation failed against GitHub's GraphQL schema (`fullDatabaseId` undefined). The workaround introduced no source changes and did not rewrite history.

## Pre-merge review and regression correction

Radar performed a structured operator self-review because an independent subagent reviewer was not available in this runtime. The review found one blocking semantic mismatch before merge:

- Python `DependencyGraph.ready()` returned false for an assignment with no predecessors.
- Installed SQL `radar.assignment_ready()` correctly returns true when no active predecessor blocks the assignment.

TDD receipt:

1. Regression added first: root assignment with no predecessors must be READY.
2. CI #117 failed exactly on that regression on Python 3.11 and 3.12: `1 failed, 85 passed`.
3. Minimal Python fix removed the incorrect non-empty-predecessor requirement.
4. CI #119 passed on Python 3.11 and 3.12.
5. Cutover PR #3 re-ran the same source as CI #121 and passed on Python 3.11 and 3.12, including compileall, the full 86-test suite, and migration source-hash emission.

No Supabase migration, seed, or repair source changed during this correction.

## Canonical merge readback

PR #3 was merged with expected head SHA protection. GitHub readback reported:

- merged: true
- source head: `e52639a25ce9b5f68831659c3c3500ba0384124c`
- merge commit: `1b47b32b9d5a4badd2af5e9943be75be61e1c143`

A fresh branch inventory after merge showed `main` at the cutover merge commit and retained all required writer lanes, protocol lineage, integration history, predecessor feature branches, Brigit's legacy-spelled lane, and the temporary diagnostic branch. No branch deletion or history rewrite occurred.

## Provider post-cutover reconciliation

Fresh read-only Supabase readback against project `klmbpaigzeguvnpccqzz`, schema `radar`, reported:

- schema exists: true
- base tables: 14
- `anon` schema usage: false
- `authenticated` schema usage: false
- identity `radar`: ACTIVE
- identity `vera`: ACTIVE with alias `vera-sol`
- historical identity `vera-sol`: ARCHIVED with successor `vera`
- endpoint `lane-vera`: ACTIVE at `bus/vera-sol-v1`
- historical endpoint `lane-vera-sol`: ARCHIVED with original address preserved in metadata
- Realtime membership exactly: `acknowledgements`, `assignments`, `dependencies`, `nodes`, `reconciliation_events`
- temporary transactional-test identity rows: 0
- temporary transactional-test assignment rows: 0
- temporary transactional-test DLQ rows: 0

Result: no material provider drift detected during the Phase 19 reconciliation.

## Post-cutover canonical maintenance

After merge, Radar made canonical-only truth updates on `main`:

- CI now runs on canonical `main` pushes in addition to PRs and Radar integration branches.
- README now identifies `main` as the Radar V1 canonical line and records the cutover source/merge provenance.
- `architecture/contracts/RADAR_CURRENT.json` is promoted separately through a final-verification-pending state and then to final verified canonical state only after exact-head CI/readback.

## Remaining gate

At the time this receipt is created, exact-head post-cutover CI/readback for the final canonical status commit is still pending. Do not infer final verification from this document alone; consult `architecture/contracts/RADAR_CURRENT.json` and the latest `main` workflow run.
