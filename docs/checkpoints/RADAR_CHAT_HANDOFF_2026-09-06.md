# Radar chat handoff checkpoint — 2026-09-06

Status: `SOURCE IMPLEMENTED / ANCHOR D SOURCE-BOUND / EXECUTABLE QUALIFICATION BLOCKED / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN`.

This checkpoint records the post-conflict-resolution state recovered from the full Radar chat handoff. It is continuation evidence only. It does not authorize merge, rebase/history rewrite, provider migration, Edge deployment/configuration, cursor seeding, dispatcher activation on canonical `main`, billing/account changes, credential/ruleset changes, or any other protected/live effect.

## Current Git state

- Canonical `main`: `87df9b1372d0f65b5c3ced0296122b2140084024`, tree `db73fcc73922447f0f19955c3a494e99030d4dca`.
- Consolidated staging branch: `radar/reproducible-ci-source-custody-v1-20260906`.
- Verified pre-checkpoint staging head: `29ba509700e6cccf85f6641f0227a8f103042bfb`, tree `d8451603736ed80903892a097ab3c1467cd68818`.
- Commit `29ba5097...` is the post-merge cleanup: `fix: restore coherent Radar currentness after conflict merge`.
- The formerly open source-hardening stack PRs #35–#41 now show closed/merged. PR #41 merged the Anchor-D successor into the staging branch; `main` remains unchanged by that stack.
- Comparing `main@87df9b13...` to staging `29ba5097...` yields `diverged`, `ahead_by: 94`, `behind_by: 1`, merge base `b1c0ceb80c6ce895927cd715319257b28124d919`. Do not treat staging as a fast-forward candidate.

Creating this checkpoint advances the staging branch beyond `29ba5097...`; fresh-read the branch head before any subsequent write.

## Conflict-resolution verification

The seven PR #41 successor paths were fresh-read after the merge conflict resolution:

1. `.github/workflows/radar-central-dispatcher.yml`
2. `architecture/contracts/RADAR_CURRENT.json`
3. `architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V3.json`
4. `architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json`
5. `docs/checkpoints/RADAR_RESTORE_2026-09-06.md`
6. `tests/security/test_projection_anchor_c_consistency.py`
7. `tests/security/test_projection_anchor_d_consistency.py`

The earlier duplicate `uses:` damage in `radar-central-dispatcher.yml` is no longer present. The dispatcher contains exactly one reusable-workflow call pinned to Anchor D:

`401733b2013802880320629a4d8ea06f8bf7b760`

`RADAR_CURRENT.json` no longer contains the duplicated schema/currentness/provider-drift fields introduced during conflict resolution. Its current source model is coherent:

- Anchor B: historical.
- Anchor C: historical.
- Anchor D: current source-only projection anchor.
- Anchor D tree: `d3a9c44f0378409a626e29334b4d057ef20c7e8e`.
- projection trust contract: `RADAR_PROJECTION_TRUST_ANCHOR_V3.json`.
- V3 trust receipt is included in source custody.
- provider drift names Anchor D as not deployed and no longer treats C as current.

The historical-C regression requires B→C→D lineage. The D regression requires dispatcher, V3 trust receipt, `RADAR_CURRENT`, custody, and provider-drift naming to agree on D exactly.

## Verification state

There is no workflow run associated with exact pre-checkpoint head `29ba509700e6cccf85f6641f0227a8f103042bfb`. Therefore no exact-head executable qualification exists for the repaired consolidated staging state.

Issue #39 remains OPEN: private-repository GitHub Actions jobs have been failing before runner assignment with `runner_id: 0`, empty `steps`, and no executable logs. Public controls under the same owner have executed normally. The exact account/private-repository cause remains unverified.

Do not call the staging source GREEN/runtime-qualified until a newly triggered exact-candidate run actually receives a hosted runner and completes the Python 3.11/3.12, SQL reset/assertion, and Edge frozen-lock jobs to code-level results.

## Provider/live boundary

Issue #16 remains OPEN.

Last source-recorded provider state remains:

- provider Radar migration ledger stops at `20260903113314_radar_operator_views_v1`;
- five later Radar source migrations remain unapplied;
- live `github-bus-ingest` is version 3, ACTIVE, with `verify_jwt=true`;
- body-bound central GitHub OIDC Edge source is not deployed;
- projection journal/replay-guard provider objects and lane cursors are not established;
- Anchor D is source-only and provider `RADAR_TRUSTED_PROJECTOR_SHA` is not established for D by this work;
- central dispatcher is not active on canonical `main`.

No provider/live effect was performed during this restore.

## Exact continuation frontier

1. Fresh-read the staging head created by this checkpoint and re-confirm the seven conflict-sensitive paths if another writer has moved the branch.
2. Establish an executable exact-head qualification path for the consolidated staging candidate without changing billing/account settings unless Patrick separately authorizes such a change after preserving the decisive GitHub UI/account evidence.
3. If private runners recover, run the full exact-head Python 3.11/3.12 + SQL + Edge matrix and then rerun hostile invariants on that same head.
4. Keep issue #16/provider recovery unapplied until separate protected-effect authorization exists.
5. Before any integration toward `main`, reconcile the `94 ahead / 1 behind` divergent history deliberately; do not blindly merge conflict choices or rewrite history.

Recommended restore command:

`RADAR::RESTORE::CHAT_HANDOFF_2026-09-06 — Read docs/checkpoints/RADAR_CHAT_HANDOFF_2026-09-06.md from the current head of radar/reproducible-ci-source-custody-v1-20260906, fresh-read main, the staging head, exact-head CI, issues #16/#39, and the conflict-sensitive Anchor-D files, then continue from the executable-qualification/divergent-history boundary. Do not invent GREEN evidence and do not merge/rebase/deploy/apply protected effects without Patrick's explicit authorization.`
