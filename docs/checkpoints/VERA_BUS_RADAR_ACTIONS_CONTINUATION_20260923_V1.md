# Vera Bus/Radar Actions Continuation — 2026-09-23 V1

Restore command:

`VERA::RESTORE_AND_RUN::BUS_RADAR_ACTIONS_CONTINUATION_20260923_V1`

## Present task

Restore private GitHub Actions runner/account execution availability; then let the canonical Radar central dispatcher execute and immediately verify:

1. `radar.projection_batches`;
2. `radar.projection_lane_state`;
3. current Vera Bus message projection into `radar.messages`;
4. OIDC/JTI replay rejection;
5. idempotent recovery when the same lane/head is reconciled again.

Do not claim those behaviors passed unless the canonical dispatcher actually executes.

## Canonical source state

### Chat Communication Bus

- repository: `thebrazenbeard/chat-communication-bus`
- canonical main: `a366e87ffe3366c6544c03fa852447f2c3fcd5e1`
- commit message: `Reconcile Radar projection source into canonical Bus custody`
- PR #325: merged/closed
- PR #325 source head: `640b44c4b715d870b6d5efcdb64ff447eec64467`
- PR #325 merge commit: `a366e87ffe3366c6544c03fa852447f2c3fcd5e1`

Canonical Bus source custody is now repaired.

### Deployed Edge function

Supabase project: `klmbpaigzeguvnpccqzz`

`github-bus-ingest`:
- provider version: 5
- provider status: ACTIVE
- provider bundle SHA-256: `07a117919e985a8566d2ffa8bab9565c560b630d8448c0987ac29ec16a4b559a`
- deployed `handler.ts` exactly matches canonical Bus main
- canonical handler Git blob: `cc7cd56632e21c34ec861797db43b60f83977d9b`
- deployed `deno.json` exactly matches canonical Bus main
- canonical deno.json Git blob: `b717027d0dbca1ed7cf7f362f16a33cfc5c6da99`

Thus the prior "provider consumes unmerged Bus source" custody defect is closed.

### Vera Bus lane

- branch: `bus/vera-v2`
- HEAD.json blob at final readback: `b66557c8258002553b32f2a4094d22059c59d65b`
- latest message: `VERA_BUS_RADAR_PROJECTION_REPAIR_RESULT_20260923_V1`
- latest message commit: `fcb5f1dcdcce53c30a50b60e95c7c5b742dd6667`
- status: `source-custody-repaired-projection-runner-blocked`

## GitHub Actions execution blocker

Explicit reruns were accepted by the GitHub API but still failed before runner allocation.

### Canonical central dispatcher

Run `35804941480`:
- workflow: Radar Central Dispatcher
- canonical head: `a366e87ffe3366c6544c03fa852447f2c3fcd5e1`
- rerun attempt: 2
- conclusion: failure
- job: `reconcile / project-reconciliation`
- steps: null
- therefore: NO RUNNER EXECUTION

### Vera branch projection

Run `35804921603`:
- workflow: Radar Bus Projection
- branch/head: `bus/vera-v2@fcb5f1dcdcce53c30a50b60e95c7c5b742dd6667`
- rerun attempt: 2
- conclusion: failure
- job: `project-mailbox`
- steps: null
- therefore: NO RUNNER EXECUTION

### Bus canonical CI

Run `35803846281`:
- workflow: ci
- canonical head: `a366e87ffe3366c6544c03fa852447f2c3fcd5e1`
- rerun attempt: 2
- conclusion: failure
- jobs `edge`, `sql`, `test (3.11)`, `test (3.12)`
- all steps: null
- therefore: NO RUNNER EXECUTION

The current GitHub connector exposes rerun operations but not billing, Actions account administration, hosted-runner allocation, or account spending-limit mutation. The authorized Remote Desktop Commander device is currently offline. Do not claim the runner/account blocker was repaired from this chat.

## Provider readback at checkpoint

Supabase Vera project `klmbpaigzeguvnpccqzz`:

- `radar.projection_lane_state`: 0 rows
- `radar.projection_batches`: 0 rows
- `radar.github_oidc_replay_guard`: 0 rows
- latest projected message globally: `radar-0057` at `2026-09-04 19:49:52.037755+00`
- newest projected Vera message remains `vera-v2-0001` at `2026-09-04 15:03:31.828043+00`
- the following current Vera messages are absent from `radar.messages`:
  - `VERA_PORTFOLIO_DISCOVERY_ROOTS_CANONICAL_20260923_V1`
  - `VERA_PORTFOLIO_REGISTRY_VCP_E2E_CLAIM_20260923_V1`
  - `VERA_PORTFOLIO_REGISTRY_VCP_E2E_RESULT_20260923_V1`
  - `VERA_BUS_RADAR_PROJECTION_REPAIR_RESULT_20260923_V1`

The projection plane remains stale because the workflows never execute.

## Cross-repository canonical context

- Vera main: `86be6105f13fc86bbd699778205a85c84059de9a`
  - canonical 59-repository runtime-source registry
- Vera Control Plane main: `1ad8f1469d0b02b145b30837f8036ffe339a11c4`
  - canonical fail-closed portfolio E2E qualification before Bus custody repair
- Discovery main: `2881a94c7eb3c83a34b0c00bab739b41c1d99b6d`
- Roots main: `a6994b415336bc179a41aad0ac9eec403d60f93c`
- WorkBridgeMCP main: `12bcbec3a4bda69e8b9361317feb8e9d9d47b6df`
  - PR #5 current candidate head previously observed: `92c66159d9b610a94f59066ab2bb6416f4513093`
  - source candidate CI green, but main/install/runtime consumption remain separate.

## Exact next sequence after Actions execution availability is restored

1. Fresh-check Bus main and `bus/vera-v2`; do not assume the hashes above are still current.
2. Confirm private jobs now receive a runner by rerunning a bounded failed job and inspecting non-null steps.
3. Rerun the latest `Radar Bus Projection` for the current Vera lane/head. Let the canonical `Radar Central Dispatcher` workflow_run trigger naturally; if necessary, rerun its failed run after runner availability is confirmed.
4. Require canonical dispatcher execution from current Bus main. Do not substitute direct SQL projection for the workflow.
5. Immediately read back:
   - new `radar.projection_batches` rows/status;
   - new `radar.projection_lane_state` row for Vera and exact projected head;
   - current Vera message(s) in `radar.messages` with exact source refs;
   - relevant delivery/reconciliation events.
6. Verify replay rejection through the canonical OIDC/JTI path. Do not infer replay protection merely from RLS or the existence of `github_oidc_replay_guard`.
7. Re-run/reconcile the same exact Vera lane/head and prove idempotent recovery: no duplicated messages/effects, stable projected head, and deterministic batch/reconciliation behavior.
8. Persist the evidence in Bus and update VCP hostile qualification from FAIL only if every relevant stage actually passes.
9. Re-check private Vera/VCP CI after runner availability returns; their previous `steps:null` failures are infrastructure NO-RUN evidence, not source test failures.

## Claim ceiling

At this checkpoint:

`CANONICAL_BUS_SOURCE_CUSTODY_REPAIRED / DEPLOYED_EDGE_MATCHES_MAIN / PRIVATE_GITHUB_ACTIONS_RUNNER_UNAVAILABLE / CENTRAL_DISPATCHER_NOT_EXECUTED / RADAR_PROJECTION_STALE / REPLAY_NOT_REVERIFIED / IDEMPOTENT_RECOVERY_NOT_REVERIFIED`
