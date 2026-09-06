# Radar chat handoff checkpoint — 2026-09-06

Status: `SOURCE IMPLEMENTED / ANCHOR D SOURCE-BOUND / LOCAL EXECUTABLE QUALIFICATION PENDING / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN`.

This checkpoint records the post-conflict-resolution state recovered from the full Radar chat handoff plus the no-paid qualification correction. It is continuation evidence only. It does not authorize merge, rebase/history rewrite, provider migration, Edge deployment/configuration, cursor seeding, dispatcher activation on canonical `main`, billing/account changes, credential/ruleset changes, or any other protected/live effect.

## Current Git state

- Canonical `main`: `87df9b1372d0f65b5c3ced0296122b2140084024`, tree `db73fcc73922447f0f19955c3a494e99030d4dca`.
- Consolidated staging branch: `radar/reproducible-ci-source-custody-v1-20260906`.
- Post-merge cleanup head: `29ba509700e6cccf85f6641f0227a8f103042bfb`, tree `d8451603736ed80903892a097ab3c1467cd68818`.
- First restore-checkpoint head: `87574118c423c3aa4e3955fa586a8af418e43ae8`, tree `4e5a8955a663ed69becb1e777659c681db271b99`.
- CI-evidence correction head: `a939fab266d01c6343e9318ae00752c27cbaa897`.
- No-paid local runner initial commit: `8471c3314b1656c46a13abebfdbb83d7aae1884e`.
- No-paid operator contract commit: `3262ab318132bb49757767d894862bcb5b09b05c`.
- Clean exact-tree receipt hardening head before this checkpoint update: `9efc10da93ffc9f30ba37da6ed3bd4b8bb269c0b`, tree `a345bea261931edfcc15cdc5525ba4c308a89172`.
- The formerly open source-hardening stack PRs #35–#41 show closed/merged into the staging branch. PR #41 merged the Anchor-D successor into staging; `main` remains unchanged by that stack.
- Comparing `main@87df9b13...` to staging at the post-merge cleanup yielded `diverged`, `ahead_by: 94`, `behind_by: 1`, merge base `b1c0ceb80c6ce895927cd715319257b28124d919`. Do not treat staging as a fast-forward candidate.

Creating/updating this checkpoint advances staging beyond `9efc10da...`; fresh-read branch head before any subsequent write.

## Conflict-resolution verification

The seven PR #41 successor paths were fresh-read after merge conflict resolution:

1. `.github/workflows/radar-central-dispatcher.yml`
2. `architecture/contracts/RADAR_CURRENT.json`
3. `architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V3.json`
4. `architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json`
5. `docs/checkpoints/RADAR_RESTORE_2026-09-06.md`
6. `tests/security/test_projection_anchor_c_consistency.py`
7. `tests/security/test_projection_anchor_d_consistency.py`

The duplicate `uses:` damage in `radar-central-dispatcher.yml` is gone. Dispatcher contains one reusable-workflow call pinned to Anchor D:

`401733b2013802880320629a4d8ea06f8bf7b760`

`RADAR_CURRENT.json` is coherent:

- Anchor B: historical.
- Anchor C: historical.
- Anchor D: current source-only projection anchor.
- Anchor D tree: `d3a9c44f0378409a626e29334b4d057ef20c7e8e`.
- projection trust contract: `RADAR_PROJECTION_TRUST_ANCHOR_V3.json`.
- V3 trust receipt is included in source custody.
- provider drift names Anchor D as not deployed and no longer treats C as current.

The historical-C regression requires B→C→D lineage. The D regression requires dispatcher, V3 trust receipt, `RADAR_CURRENT`, custody, and provider-drift naming to agree on D exactly.

## Private GitHub Actions evidence

The initial restore incorrectly stated that no workflow run existed for `29ba509700e6cccf85f6641f0227a8f103042bfb`. That came from a connector action exposing only pull-request-triggered runs. Branch-level Actions enumeration exposed push-triggered runs.

Three exact staging heads reproduced the same pre-runner failure:

- `29ba509700e6cccf85f6641f0227a8f103042bfb` — CI run `34057664601`;
- `87574118c423c3aa4e3955fa586a8af418e43ae8` — CI run `34058064585`;
- `a939fab266d01c6343e9318ae00752c27cbaa897` — CI run `34059843334`.

Across those runs, SQL, Python 3.11, Edge, and Python 3.12 jobs terminated with failure before executable steps. Step sets were empty/null and at least one job-log read returned `BlobNotFound`, consistent with no hosted runner execution beginning.

This is infrastructure evidence, not source/test failure evidence.

## No-paid qualification correction

Patrick restated the standing constraint to avoid paid services. Therefore private GitHub-hosted Actions must not be treated as a required Radar qualification dependency, and billing/payment/spending-limit changes are not a valid Radar recovery path.

The source-bound local replacement is:

- `scripts/radar_local_qualify.ps1`
- `docs/operator/RADAR_NO_PAID_QUALIFICATION.md`

It reproduces the substantive `.github/workflows/ci.yml` recipe locally with:

- Python 3.11 and 3.12;
- pip 26.2.1;
- Deno 2.9.6;
- Supabase CLI 2.116.0;
- Docker/local Supabase;
- `psql` over every `supabase/tests/radar_*.sql` assertion.

The runner fails closed if the required commands are absent, the frozen versions do not match, the working tree is dirty, or any command fails. A PASS receipt binds the exact Git commit and Git tree.

This path is source-implemented but has not yet been executed on a local machine with the frozen toolchain. Therefore status is `LOCAL EXECUTABLE QUALIFICATION PENDING`, not GREEN.

Issue #39 remains open as historical/infrastructure evidence for the private hosted-runner pre-run failures. Radar's resolution is replacement of the paid-capable dependency, not purchase of runner capacity. Public hosted Actions may be used only for deliberately public, non-secret verification payloads; do not publish private repository source merely to obtain free CI.

## Bus coordination

Radar checked sender lanes rather than only its own lane. Vera's current `bus/vera-v2` had no direct Vera→Radar message at the time of the check. One had outstanding Radar-directed material, including `one-0061`, `one-0073`, and `one-0074`.

Radar replied on `bus/radar-v2` with:

- `messages/0066-radar-to-one-r10a1-static-review-and-no-paid-ci.md`
- commit `7ec22dfe842608bcff2e4fc269294fd7fdbcdd8a`

The reply preserves static/runtime separation, accepts no runtime promotion, and propagates the no-paid qualification constraint.

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

No provider/live effect was performed during this restore, CI investigation, no-paid-path implementation, or Bus reply.

## Exact continuation frontier

1. Fresh-read staging head after this checkpoint update.
2. Execute `scripts/radar_local_qualify.ps1` on a local Windows machine with the exact frozen toolchain and a clean checkout of one exact staging candidate; capture the PASS/FAIL receipt tied to commit + tree.
3. If local qualification passes, rerun hostile/source invariants against that same exact head before any status promotion.
4. Keep issue #16/provider recovery unapplied until separate protected-effect authorization exists.
5. Before any integration toward `main`, deliberately reconcile the staging/main divergent history; do not blindly merge conflict choices or rewrite history.
6. Do not pursue paid GitHub Actions capacity, billing/payment changes, or public mirroring of private source as a workaround.

Recommended restore command:

`RADAR::RESTORE::CHAT_HANDOFF_2026-09-06 — Read docs/checkpoints/RADAR_CHAT_HANDOFF_2026-09-06.md from the current head of radar/reproducible-ci-source-custody-v1-20260906, fresh-read main, staging, the local no-paid qualification runner/contract, issues #16/#39, sender-lane messages addressed to Radar, and the conflict-sensitive Anchor-D files. Continue from the local executable-qualification/divergent-history boundary. Do not invent GREEN evidence and do not merge/rebase/deploy/apply protected effects without Patrick's explicit authorization.`
