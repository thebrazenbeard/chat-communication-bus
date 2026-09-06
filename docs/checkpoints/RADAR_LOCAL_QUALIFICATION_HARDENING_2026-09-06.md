# Radar local qualification hardening checkpoint — 2026-09-06

Status: `SOURCE IMPLEMENTED / ANCHOR D SOURCE-BOUND / NO-PAID LOCAL QUALIFICATION SAFETY-HARDENED / MAIN DELTA CONTENT-RECONCILED / LOCAL EXECUTABLE QUALIFICATION PENDING / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN`.

This is continuation/source evidence only. It does not authorize merge, rebase/history rewrite, provider migration, Edge deployment/configuration, cursor seeding, dispatcher activation on canonical `main`, billing/account changes, credential/ruleset changes, or any other protected/live effect.

## Snapshot

Immediately before this checkpoint was created, consolidated staging was:

- branch: `radar/reproducible-ci-source-custody-v1-20260906`
- commit: `605e2baace8e10e02af0fb32ebcb0f6f86df8976`
- tree: `4da0efbc22b1dcb3401d6b5e3d4b34c90687b4d1`

Fresh-read the branch before any successor write.

Canonical `main` remains `87df9b1372d0f65b5c3ced0296122b2140084024`. The previously observed one-commit ancestry delta remains content-reconciled by `docs/checkpoints/RADAR_MAIN_DIVERGENCE_RECONCILIATION_2026-09-06.md`; do not replay/cherry-pick it merely to recover source payload.

## Local no-paid qualification safety state

The authoritative source path remains:

- `architecture/contracts/RADAR_QUALIFICATION_V1.json`
- `scripts/radar_local_qualify.ps1`
- `docs/operator/RADAR_NO_PAID_QUALIFICATION.md`
- `tests/security/test_no_paid_qualification_consistency.py`

The runner now fails closed on all of the following local-state hazards before it can emit PASS:

1. dirty checkout before qualification;
2. source commit/tree/worktree drift during qualification;
3. receipt path resolving inside the checkout;
4. required tool/version mismatch;
5. any Python/Deno/SQL assertion failure;
6. an already-running local Supabase stack;
7. retained exact DB container `supabase_db_chat-communication-bus`;
8. retained exact DB volume `supabase_db_chat-communication-bus`;
9. any pre-existing Docker container, volume, or network labeled `com.supabase.cli.project=chat-communication-bus`;
10. local Supabase teardown failure.

The explicit DB container/volume probes remain in addition to the project-label-wide probes so retained/legacy resources are protected even if they lack current Supabase CLI labels.

Cleanup is armed only after the complete preflight passes, but before `supabase start`, so a partial qualification startup is cleaned. A cleanup-only failure is fatal. If SQL/start failure and cleanup failure both occur, the runner preserves and reports both causes rather than allowing teardown failure to erase the primary failure.

The Supabase project identity is bound to checked-in `supabase/config.toml` (`project_id = "chat-communication-bus"`) by the qualification consistency suite.

## Python dependency repeatability

`pyproject.toml` is already source-custodied. Its test dependency graph is now exact-version pinned:

- pytest 9.1.1
- colorama 0.4.6 on Windows
- iniconfig 2.3.0
- packaging 26.3
- pluggy 1.6.0
- Pygments 2.21.0
- build backend setuptools 84.0.0

This closes later resolver-version drift while retaining the existing `pip install -e .[test]` recipe in both local qualification and the CI workflow.

Python artifact hashes are not yet source-locked. Do not describe this as a wheel-byte/hash-locked Python supply chain. The Deno graph remains separately lockfile-bound.

## Evidence boundary

The new safety and dependency invariants are pinned in source regression tests, and the edited TOML parses correctly. They have not been executed by the authoritative local qualification suite in this runtime.

This ChatGPT runtime still lacks the frozen local toolchain needed for authoritative execution: Windows PowerShell, Python 3.11/3.12, Deno 2.9.6, Supabase CLI 2.116.0, Docker, and `psql`. Static/source-contract verification is not GREEN qualification.

Issue #39 remains open until a clean exact-commit/tree local PASS receipt exists and private hosted Actions remain non-authoritative/opportunistic. No paid runner/billing recovery is required or permitted by the Radar no-paid policy.

Issue #16 remains open and provider/live recovery remains untouched.

## Continuation frontier

1. Fresh-read staging and sender-lane messages addressed to Radar.
2. On a suitable Windows machine, check out one exact clean staging candidate and run `scripts/radar_local_qualify.ps1`, writing any receipt outside the checkout.
3. Treat PASS only as qualifying the exact commit/tree named in that receipt.
4. If local execution exposes a defect, preserve RED evidence and repair source before retrying.
5. Do not merge to `main`, alter protected history, apply provider migrations, deploy Edge/config, seed cursors, activate dispatcher, or change billing/account settings without Patrick's separate explicit authorization.
