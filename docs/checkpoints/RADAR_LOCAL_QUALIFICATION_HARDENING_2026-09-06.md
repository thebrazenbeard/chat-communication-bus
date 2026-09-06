# Radar local qualification and trusted-ref hardening checkpoint — 2026-09-06

Status: `SOURCE IMPLEMENTED / ANCHOR D SOURCE-BOUND / NO-PAID LOCAL QUALIFICATION SAFETY-HARDENED / TRUSTED WRITER OBSERVATION REF-READ-ONLY / MAIN DELTA CONTENT-RECONCILED / LOCAL EXECUTABLE QUALIFICATION PENDING / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN`.

This is continuation/source evidence only. It does not authorize merge, rebase/history rewrite, provider migration, Edge deployment/configuration, cursor seeding, dispatcher activation on canonical `main`, billing/account changes, credential/ruleset changes, or any other protected/live effect.

## Snapshot

Immediately before this checkpoint update, consolidated staging was:

- branch: `radar/reproducible-ci-source-custody-v1-20260906`
- commit: `11f6590f083863f181bb64bb3c72b2283416f1c3`
- tree: `5f1d4af16f0cb886e374b4c80d2906209dd95278`

Fresh-read the branch before any successor write.

Canonical `main` remains `87df9b1372d0f65b5c3ced0296122b2140084024`. The previously observed one-commit ancestry delta remains content-reconciled by `docs/checkpoints/RADAR_MAIN_DIVERGENCE_RECONCILIATION_2026-09-06.md`; do not replay/cherry-pick it merely to recover source payload.

## Local no-paid qualification safety state

The authoritative source path remains:

- `architecture/contracts/RADAR_QUALIFICATION_V1.json`
- `scripts/radar_local_qualify.ps1`
- `docs/operator/RADAR_NO_PAID_QUALIFICATION.md`
- `tests/security/test_no_paid_qualification_consistency.py`

The runner fails closed on dirty source, source commit/tree/worktree drift, receipt paths inside the checkout, frozen-toolchain mismatch, Python/Deno/SQL assertion failure, pre-existing local Supabase state, and teardown failure.

Local Supabase destructive ownership is guarded before cleanup is armed:

1. already-running local stack refuses qualification;
2. retained exact DB container `supabase_db_chat-communication-bus` refuses qualification;
3. retained exact DB volume `supabase_db_chat-communication-bus` refuses qualification;
4. any pre-existing Docker container, volume, or network labeled `com.supabase.cli.project=chat-communication-bus` refuses qualification.

Cleanup is armed only after those preflight checks, but before `supabase start`, so a partial qualification startup is still cleaned. Cleanup-only failure is fatal. If SQL/start failure and cleanup failure both occur, both causes are preserved.

The Supabase project identity is bound to checked-in `supabase/config.toml` (`project_id = "chat-communication-bus"`) by the qualification consistency suite.

## Python dependency repeatability

`pyproject.toml` is source-custodied and the test dependency graph is exact-version pinned:

- pytest 9.1.1
- colorama 0.4.6 on Windows
- iniconfig 2.3.0
- packaging 26.3
- pluggy 1.6.0
- Pygments 2.21.0
- build backend setuptools 84.0.0

This closes later resolver-version drift while retaining the existing `pip install -e .[test]` recipe. Python artifact hashes are not source-locked; do not describe this as a wheel-byte/hash-locked Python supply chain. The Deno graph remains separately lockfile-bound.

## Trusted writer-ref observation hardening

A source audit found that both trusted reconciliation entrypoints used `materialize_inert_remote_bus_refs()`, which copied fetched `refs/remotes/origin/bus/*` observations into mutable local `refs/heads/bus/*` with `git update-ref` before reconciliation.

That local-head mutation is no longer part of either trusted path:

- `LocalGitRepository` now supports an explicit `use_remote_tracking_refs=True` read mode;
- `scripts/radar_trusted_reconcile.py` reads writer heads directly from `refs/remotes/origin/<writer-branch>`;
- `scripts/radar_trusted_project.py` does the same for the provider-capable projector;
- neither entrypoint imports or calls a writer-ref materializer;
- `src/radar/trusted_wakeup.py` no longer contains or exports the materialization helper, imports `subprocess`, or contains a `git update-ref`/local-writer-head mutation path.

The regression `tests/radar/test_remote_ref_reconciler.py` is source-custodied and requires:

1. a remote-tracking writer ref can be read without creating a local writer branch;
2. both trusted entrypoints opt into remote-tracking ref reads and contain no materialization helper reference;
3. `trusted_wakeup.py` exposes no local writer-ref materialization primitive;
4. the trusted projector's canonical checkout uses exact `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1`, `ref: main`, `path: canonical`, `fetch-depth: 0`, and `persist-credentials: false`.

The exact pinned `actions/checkout` source was inspected. At this SHA, `fetch-depth <= 0` uses its all-history refspec `+refs/heads/*:refs/remotes/origin/*`, so the canonical checkout supplies the `origin/bus/*` remote-tracking refs that the read-only adapter consumes.

`RADAR_SOURCE_CUSTODY_V1` is now version 7. It includes the remote-ref regression and its own custody-consistency verifier.

## Evidence boundary

The edited trusted Python payloads (`trusted_wakeup.py`, `radar_trusted_reconcile.py`, `radar_trusted_project.py`, and the remote-ref regression) were syntax-parsed successfully from the exact source payloads written in this session. Committed source was also re-read after mutation-helper removal and remote-ref regression hardening.

This is not an authoritative pytest or full qualification receipt. This runtime still lacks the complete frozen local Windows qualification toolchain. Static/source-contract and syntax evidence must not be promoted to GREEN qualification.

Issue #39 remains open until a clean exact-commit/tree local PASS receipt exists and private hosted Actions remain non-authoritative/opportunistic. No paid runner/billing recovery is required or permitted by the Radar no-paid policy.

Issue #16 remains open and provider/live recovery remains untouched.

## Continuation frontier

1. Fresh-read staging and sender-lane messages addressed to Radar.
2. Continue source-side audits only where they materially reduce qualification or trusted-projection risk.
3. On a suitable Windows machine, check out one exact clean staging candidate and run `scripts/radar_local_qualify.ps1`, writing any receipt outside the checkout.
4. Treat PASS only as qualifying the exact commit/tree named in that receipt.
5. If local execution exposes a defect, preserve RED evidence and repair source before retrying.
6. Do not merge to `main`, alter protected history, apply provider migrations, deploy Edge/config, seed cursors, activate dispatcher, or change billing/account settings without Patrick's separate explicit authorization.
