# Writer Lane V2 Zero-Gap Implementation Plan Amendment

This amendment supersedes the cutover ordering in `2026-09-03-writer-lane-v2-migration.md` wherever the original plan would change current topology before successor branches have been created and verified.

## Source-readiness PR — current implementation branch

The source-readiness PR contains:

- topology-bound exact writer-lane identity primitives;
- mailbox-only append validation across the full observed Git push range;
- declared `writer:` mismatch rejection;
- projection-emitter integration using topology identity and GitHub pre-push SHA;
- an inherited writer-lane guard workflow for future successor branches;
- the planned successor map and zero-gap cutover sequence;
- documentation/tests.

The source-readiness PR deliberately does **not** modify the canonical current branch values in `RADAR_TOPOLOGY_V1.json`.

Verification before its PR is review-ready:

```bash
python -m compileall -q src
python -m pytest -q
python scripts/radar_source_hashes.py
```

Then verify `main...HEAD` contains no topology current-lane switch, no message-history rewrite, no provider migration/deployment, and no protected administrative mutation.

## Protected post-merge stage A — create successors

Only after the source-readiness PR is merged with explicit authority:

1. Fresh-read canonical `main` and store its exact SHA as `cutover_main_sha`.
2. Fresh-read every predecessor current lane and record exact head SHAs.
3. Confirm no planned successor branch already exists; if one exists, stop and inspect it rather than overwrite it.
4. Create each planned successor from exactly `cutover_main_sha`:
   - Brigit `bus/brigit-v2`
   - Hephaestus `bus/hephaestus-v3`
   - Vera `bus/vera-v2`
   - all other active predecessor v1 lanes -> corresponding v2.
5. Verify every successor:

```text
successor_head == cutover_main_sha
merge_base(successor, cutover_main_sha) == cutover_main_sha
```

6. Verify every predecessor remains at the snapshotted head. Any movement requires reconciliation before proceeding.
7. Do not send ordinary messages to successor lanes yet.

## Protected post-merge stage B — topology switch PR

After all successors exist and verify:

1. Create a new ordinary source branch from the then-current `main`.
2. Update `RADAR_TOPOLOGY_V1.json` to the already-existing successors.
3. Update `RADAR_WRITER_LANE_V2_CUTOVER.json` with:
   - exact `cutover_main_sha`;
   - exact predecessor heads;
   - `successor_branches_created: true`;
   - `topology_switched: false` while the PR is open;
   - verification evidence for each successor.
4. Update branch disposition so predecessors are described as planned-to-be historical, not already historical while the PR is open.
5. Add/adjust tests requiring exact successor mappings and exact receipt evidence.
6. Run full CI and exact-head review.
7. Stop at Patrick's topology-switch merge gate.

After that PR merges, fresh-read canonical `main`, set routing to the topology-designated successors, and record a follow-up exact cutover receipt with `topology_switched: true` using a normal reviewed source change if the receipt itself requires canonical update.

## Never authorized by this amendment

- force-pushing/rebasing/deleting/renaming predecessor lanes;
- merging a writer lane to `main` merely to preserve messages;
- provider deployment or Supabase migration;
- GitHub ruleset/branch-protection mutation;
- credential/permission changes;
- bypassing Patrick's merge gate.
