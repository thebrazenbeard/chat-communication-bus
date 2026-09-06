# Radar no-paid qualification path

Status: `SOURCE-BOUND / LOCAL EXECUTION REQUIRED / PRIVATE HOSTED ACTIONS NON-AUTHORITATIVE`.

Patrick's standing constraint is to avoid paid services. Private GitHub-hosted Actions therefore must not be treated as a required Radar qualification dependency, and billing/payment/spending-limit changes are not a valid recovery path for Radar.

## Authoritative no-paid path

For the current Radar source candidate, executable qualification is performed on a local machine using:

- Python 3.11;
- Python 3.12;
- pip 26.2.1;
- Deno 2.9.6;
- Supabase CLI 2.116.0;
- Docker/local Supabase;
- `psql` against the local Supabase PostgreSQL instance.

The canonical Windows runner is:

`powershell -ExecutionPolicy Bypass -File scripts/radar_local_qualify.ps1`

Optional receipt output must be written outside the source checkout so the receipt cannot invalidate its own `working_tree = CLEAN` claim. For example:

`powershell -ExecutionPolicy Bypass -File scripts/radar_local_qualify.ps1 -ReceiptPath "$env:TEMP\radar-local-qualification.json"`

Relative receipt paths resolve under the repository and are therefore rejected. The JSON receipt is also emitted on stdout and may be captured externally by the caller.

The runner fails closed when a required command is missing, when Python/Deno/Supabase versions do not match the frozen CI recipe, when any test/assertion command returns non-zero, when the source commit or tree changes during qualification, or when the working tree is dirty before or after execution.

Generated Python caches/build metadata plus Supabase CLI local state are narrowly ignored through the custody-bound `.gitignore`. Receipts and arbitrary untracked files are not ignored; unrelated checkout changes still fail qualification.

## Local Supabase safety

`supabase db reset` and `supabase stop --no-backup` are intentionally destructive to the local qualification database. The checked-in `supabase/config.toml` therefore defines the stable local project identity `chat-communication-bus`; the qualification consistency suite binds the runner's resource identity to that exact config value before the SQL stage can execute.

Before starting SQL qualification, the runner checks `supabase status`. If this project's local stack is already running, qualification aborts instead of resetting or deleting that existing local database.

A stopped local stack can retain database state in Docker even when `supabase status` is not running. The runner therefore also refuses qualification if either the exact database container or exact database volume `supabase_db_chat-communication-bus` already exists. Those explicit probes protect retained or legacy database resources even if they lack current Supabase CLI labels.

Supabase CLI 2.116.0 labels its local Docker resources with `com.supabase.cli.project=<project_id>` and uses that project label when `supabase stop --no-backup` prunes containers, named volumes, and networks. The runner therefore also lists all containers, volumes, and networks carrying `com.supabase.cli.project=chat-communication-bus` and refuses qualification if any already exist. Cleanup can only become responsible for a project resource set that was empty at preflight.

Only after all of those preflight checks pass is cleanup armed. Cleanup is armed before `supabase start`, so a partial startup failure still attempts `supabase stop --no-backup` for resources created by the qualification attempt. Cleanup failure is fatal; a PASS receipt cannot be emitted if local Supabase teardown does not complete successfully.

SQL/start failure and cleanup failure are captured separately. If both occur, qualification reports both causes rather than allowing teardown failure to replace the primary SQL/start failure. If only one occurs, that failure remains fatal.

This guard applies only to local Docker resources. It does not link, reset, migrate, or otherwise modify the hosted Supabase project.

## Qualification equivalence

The local runner reproduces the substantive commands in `.github/workflows/ci.yml` without requiring a GitHub-hosted runner:

1. Python 3.11 and 3.12 each create a clean temporary virtual environment.
2. Each installs `pip==26.2.1` and `.[test]`, runs `compileall`, the complete pytest suite, and `scripts/radar_source_hashes.py`.
3. Deno runs `deno ci` and `deno check index.ts` from `supabase/functions/github-bus-ingest` using the frozen dependency graph.
4. Local Supabase starts through Docker, rebuilds from the migration chain with `supabase db reset`, then every `supabase/tests/radar_*.sql` assertion runs with `ON_ERROR_STOP=1`.
5. Local Supabase is stopped with `--no-backup` even when SQL qualification fails after startup or startup only partially succeeds; cleanup failure fails qualification.
6. Before emitting PASS, the runner re-reads the Git commit, Git tree, and working-tree state and fails closed on drift.

A PASS receipt is valid only for the exact Git commit reported by the runner as `source_commit` and exact tree reported as `source_tree`. A receipt from another commit or tree does not qualify a successor head.

## GitHub Actions status

Private GitHub-hosted Actions may remain present as opportunistic/free-quota signal, but they are not a gating dependency and must not trigger plan, billing, payment-method, spending-limit, or other paid-service changes.

Issue #39 remains historical/infrastructure evidence for the repeated pre-runner failures. Its resolution for Radar is replacement of the paid-capable dependency with this local path, not purchase of runner capacity.

Public GitHub-hosted Actions may be used only for deliberately public, non-secret, non-sensitive verification payloads where public execution is appropriate. Do not mirror private repository source into a public repository merely to obtain free CI.

## Boundary

This operator path authorizes local verification only. It does not authorize merge, deployment, provider migration, provider configuration, cursor seeding, dispatcher activation, branch-history rewrite, billing/account changes, or any other protected/live effect.
