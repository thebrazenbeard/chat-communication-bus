# Radar no-paid qualification path

Status: `SOURCE-BOUND / LOCAL EXECUTION REQUIRED / PRIVATE HOSTED ACTIONS NON-AUTHORITATIVE`.

Patrick's standing constraint is to avoid paid services. Private GitHub-hosted Actions are therefore not a required Radar qualification dependency, and billing/payment/spending-limit changes are not a valid recovery path.

## Authority split

Python engine defines qualification semantics.

`scripts/radar_qualify.py` is the canonical qualification engine and evidence producer. It owns source binding, toolchain probes, stage ordering, destructive-local-resource guards, cleanup behavior, schema-V2 receipt construction, and external receipt writing.

PowerShell is the canonical supported Windows launcher for the currently authorized platform profile.

Launcher identity is not separately attested by the receipt.

`scripts/radar_local_qualify.ps1` is only a convenience/entry launcher. It checks for the Windows `py` launcher, invokes Python 3.11 on `scripts/radar_qualify.py`, forwards the receipt path, and propagates the engine exit code. It does not duplicate qualification semantics.

A runnable engine on another OS is not automatically an authoritative platform profile.

Receipt V2 stage evidence is required before GREEN.

## Authoritative no-paid path

The current authorized profile is Windows using:

- Python 3.11 and 3.12;
- pip 26.2.1;
- Deno 2.9.6;
- Supabase CLI 2.116.0;
- Docker/local Supabase;
- `psql` against the local Supabase PostgreSQL instance.

The normal launcher command is:

`powershell -ExecutionPolicy Bypass -File scripts/radar_local_qualify.ps1`

By default the launcher sends the receipt to `$env:TEMP\radar-local-qualification.json`, which is outside the source checkout. An explicit absolute external path may be supplied:

`powershell -ExecutionPolicy Bypass -File scripts/radar_local_qualify.ps1 -ReceiptPath "$env:TEMP\radar-local-qualification.json"`

The Python engine may also be called directly on the authorized Windows profile:

`py -3.11 scripts/radar_qualify.py --receipt-path "$env:TEMP\radar-local-qualification.json"`

An in-checkout receipt path is rejected. Generated Python caches/build metadata and narrowly scoped local Supabase CLI state may be ignored by source custody, but arbitrary receipts/untracked source changes are not a substitute for the external-receipt rule.

## Exact execution contract

The engine starts by binding the exact clean Git commit/tree. It then verifies the required toolchain and executes exactly these stage instances in order:

1. `python_compileall:3.11`
2. `python_pytest:3.11`
3. `radar_source_hashes:3.11`
4. `python_compileall:3.12`
5. `python_pytest:3.12`
6. `radar_source_hashes:3.12`
7. `deno_ci`
8. `deno_check`
9. `supabase_local_start`
10. `supabase_db_reset`
11. `all_radar_sql_assertions`
12. `supabase_local_stop`

Each required Python version receives its own temporary virtual environment. pip is upgraded to exactly 26.2.1 before `.[test]` is installed. The pinned Python test graph remains pytest 9.1.1 plus its pinned runtime dependencies in `pyproject.toml`.

Deno executes `deno ci` and `deno check index.ts` from `supabase/functions/github-bus-ingest`.

SQL assertions are every sorted `supabase/tests/radar_*.sql` file, executed through `psql` with `ON_ERROR_STOP=1`. Their exact outputs are aggregated into the single `all_radar_sql_assertions` stage evidence record.

## Local Supabase safety

`supabase db reset` and `supabase stop --no-backup` are destructive only to the local qualification database. The engine refuses to start qualification when the `chat-communication-bus` local Supabase stack is already running or when existing project Docker state could be destroyed.

Before `supabase start`, it checks:

- `supabase status` is not already healthy/running;
- exact database container `supabase_db_chat-communication-bus` does not exist;
- exact database volume `supabase_db_chat-communication-bus` does not exist;
- no container, volume, or network exists with `com.supabase.cli.project=chat-communication-bus`.

Once an owned start is attempted, `supabase stop --no-backup` is attempted in `finally`. Cleanup failure is fatal. If the primary qualification stage and cleanup both fail, both causes are preserved. No PASS receipt is emitted unless cleanup succeeds.

This path does not link, migrate, reset, or otherwise modify the hosted Supabase project.

## Receipt evidence and admission

A schema-V2 PASS receipt binds:

- exact source commit;
- exact source tree;
- `working_tree = CLEAN`;
- observed/frozen toolchain evidence;
- all twelve ordered stage-evidence records;
- canonical SHA-256 over those stage records;
- a completion timestamp no earlier than the final required stage.

Before receipt emission the engine re-reads the exact commit/tree/working-tree state and fails closed on drift.

A generated receipt is not admitted merely because it says `PASS`. Validate it from the same clean checkout:

`py -3.11 scripts/radar_validate_qualification_receipt.py "$env:TEMP\radar-local-qualification.json"`

The validator rejects an in-checkout receipt even if ignored. Git cleanliness is necessary but is not a substitute for the external-receipt boundary.

The validator also checks schema V2, PASS status, qualification mode, frozen/observed toolchain evidence, exact ordered successful stage evidence and digest, receipt completion ordering, and the current exact clean HEAD/tree.

This validator is an admission-consistency control, not independent cryptographic attestation. It prevents stale, mismatched, malformed, toolchain-drifted, stage-incomplete, or source-checkout-local receipts from being admitted accidentally; it does not independently prove that an externally supplied receipt was generated by an untampered execution.

A validator success does not itself modify `RADAR_CURRENT.json`, freeze an anchor, merge source, or authorize provider/live effects.

## GitHub Actions status

Private GitHub-hosted Actions may remain opportunistic/non-gating signal but are not authoritative qualification. A self-hosted or ad-hoc workflow used to exercise focused source tests is likewise only evidence for the exact tests it actually executes; it is not a substitute for the full authoritative engine run and admitted receipt.

Public hosted Actions may be used only for deliberately public, non-secret, non-sensitive verification payloads. Private source must not be mirrored public merely to obtain free CI.

Issue #39 remains infrastructure evidence for historical pre-runner private-hosted failures. Its Radar recovery path is the local no-paid qualification model, not purchase of runner capacity.

## Boundary

The authoritative status remains `LOCAL_EXECUTION_PENDING` until the complete frozen Windows toolchain runs `scripts/radar_qualify.py`, produces an external schema-V2 PASS receipt, and that receipt is admitted against the same exact clean checkout.

This operator path authorizes verification only. It does not authorize merge, provider migration, Edge deployment/configuration, cursor seeding, dispatcher activation, credentials/ruleset changes, branch-history rewrite, billing/account changes, native Project cutover, or any other protected/live effect.
