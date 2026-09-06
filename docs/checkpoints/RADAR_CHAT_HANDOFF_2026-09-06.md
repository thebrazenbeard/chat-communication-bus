# Radar chat handoff checkpoint — 2026-09-06

Status: `SOURCE IMPLEMENTED / ANCHOR D SOURCE-BOUND / EXECUTABLE QUALIFICATION BLOCKED / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN`.

This checkpoint records the post-conflict-resolution state recovered from the full Radar chat handoff. It is continuation evidence only. It does not authorize merge, rebase/history rewrite, provider migration, Edge deployment/configuration, cursor seeding, dispatcher activation on canonical `main`, billing/account changes, credential/ruleset changes, or any other protected/live effect.

## Current Git state

- Canonical `main`: `87df9b1372d0f65b5c3ced0296122b2140084024`, tree `db73fcc73922447f0f19955c3a494e99030d4dca`.
- Consolidated staging branch: `radar/reproducible-ci-source-custody-v1-20260906`.
- Post-merge cleanup head: `29ba509700e6cccf85f6641f0227a8f103042bfb`, tree `d8451603736ed80903892a097ab3c1467cd68818`.
- First restore-checkpoint head: `87574118c423c3aa4e3955fa586a8af418e43ae8`, tree `4e5a8955a663ed69becb1e777659c681db271b99`.
- Commit `29ba5097...` is `fix: restore coherent Radar currentness after conflict merge`.
- The formerly open source-hardening stack PRs #35–#41 now show closed/merged into the staging branch. PR #41 merged the Anchor-D successor into staging; `main` remains unchanged by that stack.
- Comparing `main@87df9b13...` to staging `29ba5097...` yielded `diverged`, `ahead_by: 94`, `behind_by: 1`, merge base `b1c0ceb80c6ce895927cd715319257b28124d919`. Do not treat staging as a fast-forward candidate.

This correction commit advances the staging branch beyond `87574118...`; fresh-read the branch head before any subsequent write.

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

## Exact-head CI evidence and connector correction

The initial restore incorrectly stated that no workflow run existed for `29ba509700e6cccf85f6641f0227a8f103042bfb`. That statement came from a connector action which only exposes pull-request-triggered runs. Branch-level Actions enumeration later exposed the push-triggered runs. The corrected evidence is:

### Cleanup head `29ba509700e6cccf85f6641f0227a8f103042bfb`

CI run `34057664601`:

- SQL job `101552404328` — failure before executable steps;
- Python 3.11 job `101552404412` — failure before executable steps;
- Edge job `101552404460` — failure before executable steps;
- Python 3.12 job `101552404503` — failure before executable steps.

### Restore-checkpoint head `87574118c423c3aa4e3955fa586a8af418e43ae8`

CI run `34058064585`:

- SQL job `101553493905` — failure before executable steps;
- Python 3.11 job `101553494025` — failure before executable steps;
- Edge job `101553494060` — failure before executable steps;
- Python 3.12 job `101553494158` — failure before executable steps.

All eight jobs returned empty/null executable-step sets. A direct step read for `101553494025` returned `[]`. Its job-log download returned GitHub `BlobNotFound`, consistent with no runner execution beginning.

This is exact-head blocker evidence, not source/test failure evidence. The repaired staging source remains unqualified rather than GREEN.

Issue #39 has been updated with this reproduction. The exact account/private-repository cause remains unverified. Do not change billing/account/repository settings without separate Patrick authorization after preserving decisive evidence.

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

No provider/live effect was performed during this restore or CI investigation.

## Exact continuation frontier

1. Fresh-read the staging head created by this correction and re-confirm the seven conflict-sensitive paths if another writer has moved the branch.
2. Treat issue #39 as actively reproduced on the consolidated staging candidate. If private runners recover, run the full exact-head Python 3.11/3.12 + SQL + Edge matrix and rerun hostile invariants on that same head.
3. Keep issue #16/provider recovery unapplied until separate protected-effect authorization exists.
4. Before any integration toward `main`, reconcile the staging/main divergent history deliberately; do not blindly merge conflict choices or rewrite history.
5. Do not promote status beyond `SOURCE IMPLEMENTED / EXECUTABLE QUALIFICATION BLOCKED / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN` until evidence changes it.

Recommended restore command:

`RADAR::RESTORE::CHAT_HANDOFF_2026-09-06 — Read docs/checkpoints/RADAR_CHAT_HANDOFF_2026-09-06.md from the current head of radar/reproducible-ci-source-custody-v1-20260906, fresh-read main, staging, branch-level push CI, issues #16/#39, and the conflict-sensitive Anchor-D files, then continue from the executable-qualification/divergent-history boundary. Do not invent GREEN evidence and do not merge/rebase/deploy/apply protected effects without Patrick's explicit authorization.`
