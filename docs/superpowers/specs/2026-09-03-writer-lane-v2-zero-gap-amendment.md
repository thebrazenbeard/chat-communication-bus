# Writer Lane V2 Zero-Gap Cutover Amendment

Date: 2026-09-03
Owner: Radar
Status: accepted correction to `2026-09-03-writer-lane-v2-migration-design.md`

This amendment supersedes only the migration sequencing in the original Writer Lane V2 design where that sequencing could make canonical topology point at successor lanes before those lanes exist. The architectural goals remain unchanged: immutable predecessor provenance, mailbox-only current lanes, topology-bound sender identity, corrected prospective Brigit spelling, and no routine writer-lane PRs to `main`.

## Corrected invariant

At every observable canonical state, every topology-designated current writer lane must already exist and be the lane ordinary routing is permitted to use.

Therefore a single PR may not both install source-readiness machinery and make nonexistent successor branches current.

## Required zero-gap sequence

1. `MERGE_SOURCE_READINESS`
   - Merge validator, guard workflow, projection hardening, tests, and the planned cutover contract.
   - Keep `RADAR_TOPOLOGY_V1.json` on the currently live predecessor lanes.
   - No successor lane is current merely because its planned name appears in the cutover contract.
2. `SNAPSHOT_PREDECESSOR_HEADS`
   - Fresh-read every current writer lane immediately before branch creation.
   - Record exact observed predecessor heads; do not infer them from stale receipts.
3. `CREATE_SUCCESSOR_BRANCHES_FROM_EXACT_MAIN`
   - Create all planned successor lanes from the same exact post-source-readiness canonical `main` SHA.
   - Because the successors descend from that cut, they inherit the mailbox guard and updated projection workflow.
   - They remain inert: do not route ordinary messages to them yet.
4. `VERIFY_SUCCESSOR_BRANCHES`
   - Verify each successor head equals the declared cut SHA and its merge-base with that cut is exact.
   - Verify no predecessor lane moved since the snapshot; reconcile any movement before proceeding.
5. `MERGE_TOPOLOGY_SWITCH`
   - On a separate reviewed source change, switch `RADAR_TOPOLOGY_V1.json` from each predecessor to its already-existing verified successor.
   - Update the cutover receipt with exact observed SHAs and state.
6. `ROUTE_NEW_MESSAGES_TO_SUCCESSORS`
   - Only after the topology-switch merge is canonical may ordinary new messages use the successors.
   - Predecessors then become immutable historical provenance.

## Transitional security/currentness ceiling

After source-readiness merges but before the topology switch, the existing predecessor lanes remain canonical. Those old branches do not retroactively inherit the new guard workflow merely because `main` has it. A message-triggering projection workflow checks out current control code from `main`, so the updated emitter can validate the observed push range and topology-bound writer identity when projection runs. This is a bounded transitional protection, not a substitute for repository rulesets or the separately accepted trusted-projector/OIDC hardening work.

Successor lanes created from post-source-readiness `main` inherit both the guard and current projection workflow. They must receive no ordinary messages until topology makes them current.

## Failure handling

- If a predecessor lane moves between snapshot and topology switch, stop that identity's cutover and reconcile the new commits before switching it.
- If a successor branch already exists, verify exact ancestry/content; never overwrite it.
- If any planned successor cannot be created or verified, leave that identity's predecessor current.
- Never make topology point at a lane that does not already exist and pass the required readback.
- No force-push, rebase, deletion, rename, provider deployment, ruleset mutation, or credential change is authorized by this amendment.
