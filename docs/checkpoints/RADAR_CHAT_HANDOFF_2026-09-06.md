# Radar chat handoff checkpoint — 2026-09-06

Status: `SOURCE IMPLEMENTED / ANCHOR D SOURCE-BOUND / NO-PAID QUALIFICATION SOURCE-BOUND AND RECEIPT-HARDENED / MAIN DELTA CONTENT-RECONCILED / LOCAL EXECUTABLE QUALIFICATION PENDING / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN`.

This checkpoint records the post-conflict-resolution state recovered from the full Radar chat handoff, the no-paid qualification correction, the main/staging content reconciliation, and the subsequent local-runner receipt/lifecycle hardening. It is continuation evidence only. It does not authorize merge, rebase/history rewrite, provider migration, Edge deployment/configuration, cursor seeding, dispatcher activation on canonical `main`, billing/account changes, credential/ruleset changes, or any other protected/live effect.

## Current Git state

- Canonical `main`: `87df9b1372d0f65b5c3ced0296122b2140084024`, tree `db73fcc73922447f0f19955c3a494e99030d4dca`.
- Consolidated staging branch: `radar/reproducible-ci-source-custody-v1-20260906`.
- Post-merge cleanup head: `29ba509700e6cccf85f6641f0227a8f103042bfb`, tree `d8451603736ed80903892a097ab3c1467cd68818`.
- CI-evidence correction head: `a939fab266d01c6343e9318ae00752c27cbaa897`.
- No-paid local runner initial commit: `8471c3314b1656c46a13abebfdbb83d7aae1884e`.
- Main-delta content reconciliation checkpoint commit: `2889c5b5383076184b62becc26f0ea7ad44180b8`.
- Trusted-reconciler stale-test repair: `3be2a608006ea2446948055416c04e7d399954fc`.
- Source-custody v6 commit: `8ad4b364f241cda6e2c56cd052ebdb60d6b5125a`.
- Stable local Supabase project identity commit: `7801d59f1f443f80adb2fb5aa06eeb7a2d1ccdd8`.
- Local Supabase lifecycle guard commit: `ca3788b9de79ae5697b6b541e3627110211b9bca`.
- Pre-checkpoint local qualification hardening head: `4a5c11c7c793592afe9450c16c5af75c4230b116`, tree `f9fc8f672faa5d6c718e5730fe7490a3a2bf758c`.
- The formerly open source-hardening stack PRs #35–#41 show closed/merged into the staging branch. PR #41 merged the Anchor-D successor into staging; `main` remains unchanged by that stack.

Fresh-read the staging branch head before any subsequent write because this checkpoint update advances it again.

## Main/staging divergence is content-reconciled

Historical compares showed staging as `diverged`, with one commit reachable from `main` but not from staging ancestry. That main-only commit is:

`87df9b1372d0f65b5c3ced0296122b2140084024`

It bundles PRs #28/#29/#30: atomic routing snapshot hardening, canonical Radar V1 dedupe semantics, and Slack relay concurrency hardening.

The complete ten-path payload of that commit was compared by Git blob identity against staging. All ten blobs are byte-identical on staging:

- `docs/protocol/RADAR_DEDUPE_V1.md` — `3b00994fc95a4cb95f49aa7d63a0b167632699d4`
- `src/chat_bus/slack_relay.py` — `1d69d51a4580a49f020fcb1314d6ad83d485605f`
- `src/radar/registry.py` — `9929b9d6bf7e9abac58131d0f9aff075a2d82247`
- `src/radar/routing.py` — `b871234677c839ff00b36ea77a498e4903444558`
- `src/radar/runtime.py` — `6c2640fd5e40249fdebf76ca5b45e9b18e7c08f4`
- `tests/chat_bus/test_slack_relay_concurrency.py` — `53bf4f134a66c764e2e4866c0145721b1790593d`
- `tests/radar/test_canonical_dedupe_contract.py` — `a615fe3811200aae29d04e610efab1e411efc754`
- `tests/radar/test_multi_audience_routing_snapshot.py` — `dd39f12e38abe7146a2f2fac8f6942280a00ce8d`
- `tests/radar/test_runtime_accounting_contract.py` — `588710d7f025af170c8333242b770218b10b9a2c`
- `tests/radar/test_runtime_pipeline.py` — `206ada156a06d3a72367a4bedc277c3aeeabbdf7`

Authoritative continuation evidence is `docs/checkpoints/RADAR_MAIN_DIVERGENCE_RECONCILIATION_2026-09-06.md`, which is included in source custody v6.

Conclusion: the one-commit `behind` count is ancestry/topology only at the verified snapshot; staging is not missing the source/test payload of main's PR #28/#29/#30 integration commit. Do not cherry-pick/replay that commit merely to recover code. Any actual integration to `main` still requires Patrick's explicit authorization and a fresh comparison.

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

## Private GitHub Actions evidence

Three exact staging heads reproduced the same pre-runner failure:

- `29ba509700e6cccf85f6641f0227a8f103042bfb` — CI run `34057664601`;
- `87574118c423c3aa4e3955fa586a8af418e43ae8` — CI run `34058064585`;
- `a939fab266d01c6343e9318ae00752c27cbaa897` — CI run `34059843334`.

Across those runs, SQL, Python 3.11, Edge, and Python 3.12 jobs terminated before executable steps. This is infrastructure evidence, not source/test failure evidence.

Private hosted Actions are non-authoritative for Radar and are not a required recovery frontier. Issue #39 remains open as the infrastructure record until the authoritative local path produces an exact commit/tree executable receipt.

## No-paid qualification contract

Patrick's standing project constraint is to avoid paid services. Radar binds this in `architecture/contracts/RADAR_QUALIFICATION_V1.json`:

- policy: `NO_PAID_SERVICES`
- authoritative mode: `LOCAL_NO_PAID_SERVICES`
- status: `LOCAL_EXECUTION_PENDING`
- private hosted Actions authoritative: false
- billing/plan recovery allowed: false
- GREEN requires a local PASS receipt bound to exact Git commit + tree from a clean worktree.

The source-bound local runner is:

- `scripts/radar_local_qualify.ps1`
- `docs/operator/RADAR_NO_PAID_QUALIFICATION.md`

It reproduces the substantive CI recipe locally with Python 3.11/3.12, pip 26.2.1, Deno 2.9.6, Supabase CLI 2.116.0, Docker/local Supabase, and `psql` over every `supabase/tests/radar_*.sql` assertion.

This path is source-implemented but has not yet been executed on a local machine with the frozen toolchain. Status remains `LOCAL EXECUTABLE QUALIFICATION PENDING`, not GREEN.

## Local qualification receipt and lifecycle hardening

The no-paid runner was audited specifically for defects that private hosted CI could not expose. The following invariants are now source-bound and regression-pinned:

1. **Post-run exact-source revalidation.** The runner captures `HEAD`, `HEAD^{tree}`, and a clean working tree before qualification, then re-reads all three after Python, Deno, and local Supabase work. It refuses PASS if the source commit, source tree, or working-tree state changed during qualification.
2. **Receipts cannot self-invalidate the source checkout.** An optional `-ReceiptPath` must resolve outside the repository. In-repository receipt paths are rejected with `Receipt path must be outside source checkout`. JSON is also emitted on stdout for external capture.
3. **Generated local state is narrowly ignored.** The custody-bound `.gitignore` permits only standard Python cache/build metadata and local Supabase CLI state: `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `*.egg-info/`, `.supabase/`, `supabase/.temp/`, and `supabase/.branches/`. Receipts and arbitrary untracked files remain visible to the clean-worktree guard.
4. **Stable local Supabase identity.** `supabase/config.toml` now defines `project_id = "chat-communication-bus"` for local Docker-resource isolation. This is a local source configuration value, not the hosted Supabase project ref.
5. **Pre-existing local Supabase data is protected.** Before SQL qualification, the runner checks `supabase status`. If this project's local stack is already running, qualification aborts rather than resetting or deleting an existing local database.
6. **Partial-start cleanup is armed before startup.** After the pre-existing-stack guard passes, cleanup is armed before `supabase start`, so a partial startup failure still attempts `supabase stop --no-backup`, matching the hosted CI intent to clean local qualification state.

These checks were developed through focused source/static RED→GREEN assertions. They have not been exercised by a real PowerShell/Deno/Supabase end-to-end run in this environment. Do not convert source/static evidence into executable qualification evidence.

Source custody is now `RADAR_SOURCE_CUSTODY_V1` version 6 and includes `.gitignore`, the no-paid qualification contract/runner, and the main-delta reconciliation checkpoint.

## Trusted local-Git reconciliation finding

The repository already contains a validate-only local-Git reconciliation path:

- `src/radar/trusted_reconciler.py` provides `LocalGitRepository` and derives ordered ancestry without executing writer-branch files.
- `scripts/radar_trusted_reconcile.py` is explicitly validate-only and performs no provider write.
- `tests/radar/test_local_git_reconciler_adapter.py` proves local Git ancestry reading and fail-closed behavior for missing writer branches.

This is not runtime message routing and not a durable local projection replacement. The current validate-only CLI uses an uninitialized cursor view, so it derives from activation anchors rather than persisting an incremental local cursor.

A safety caveat remains: `materialize_inert_remote_bus_refs()` copies `origin/bus/*` remote-tracking refs into local `refs/heads/bus/*` using `git update-ref`. That is provider-safe but mutates local branch refs. Do not treat the current CLI as safe for an ordinary working checkout without further design/hardening; use of a dedicated disposable/trusted checkout would be required as-is.

During this trace two executable-suite regressions hidden by the hosted-runner outage were found and repaired:

1. `tests/radar/test_trusted_reconcile_cli.py` still called obsolete `_requested_identities`; staging commit `3be2a608006ea2446948055416c04e7d399954fc` updates it to the current `requested_identities(..., repository=...)` API.
2. `tests/security/test_reproducible_ci_custody.py` still asserted source-custody version `2`; it was corrected and subsequently advanced with the custody contract to current version 6.

These repairs remain source evidence until the authoritative local qualification suite executes.

## Bus coordination

Radar checks sender lanes, not only its own lane. At the latest sender-lane check:

- Vera `bus/vera-v2` had advanced to `265e7b28d9ec939994dad98daa78a9205e4edd98` with no new direct Vera→Radar message filename.
- One `bus/one-v2` had advanced to `7fd70197591067df302f8943032e0eab1de2bdfd`; the only direct Radar-addressed filenames remained the previously known `0023`, `0061`, and mixed-address `0073` material, with later work through `0103` focused elsewhere.

Radar previously sent:

- `messages/0066-radar-to-one-r10a1-static-review-and-no-paid-ci.md`
- `messages/0067-radar-to-vera-one-no-paid-qualification-contract.md`
- `messages/0068-radar-to-vera-one-source-reconciliation-update.md`

No new sender-lane reply was owed at the latest check.

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

No provider/live effect was performed during this work.

## Exact continuation frontier

1. Fresh-read staging head after this checkpoint update.
2. Execute `scripts/radar_local_qualify.ps1` on a local Windows machine with the exact frozen toolchain and a clean checkout of one exact staging candidate; capture PASS/FAIL tied to commit + tree. Do not run it while this project's local Supabase stack is already running.
3. Treat `docs/checkpoints/RADAR_MAIN_DIVERGENCE_RECONCILIATION_2026-09-06.md` as proof that the previously observed `behind_by=1` delta is content-reconciled; only history integration remains protected.
4. If a local Bus observer/reconciler is desired, harden it before ordinary-checkout use; current remote-ref materialization mutates local branch refs and local cursor state is not durable.
5. Keep issue #16/provider recovery unapplied until separate protected-effect authorization exists.
6. Do not pursue paid GitHub Actions capacity, billing/payment changes, or public mirroring of private source as a workaround.

Recommended restore command:

`RADAR::RESTORE::CHAT_HANDOFF_2026-09-06 — Read docs/checkpoints/RADAR_CHAT_HANDOFF_2026-09-06.md and docs/checkpoints/RADAR_MAIN_DIVERGENCE_RECONCILIATION_2026-09-06.md from the current head of radar/reproducible-ci-source-custody-v1-20260906; fresh-read main, staging, the no-paid qualification contract/runner, issues #16/#39, sender-lane messages addressed to Radar, and the conflict-sensitive Anchor-D files. Continue from actual local executable qualification. Treat the one-commit main delta as content-reconciled. Do not invent GREEN evidence, do not run qualification against a pre-existing local Supabase stack, and do not merge/rebase/rewrite history or apply provider/live effects without Patrick's explicit authorization.`
