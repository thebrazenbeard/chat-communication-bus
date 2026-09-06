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

Optional receipt output:

`powershell -ExecutionPolicy Bypass -File scripts/radar_local_qualify.ps1 -ReceiptPath artifacts/radar-local-qualification.json`

The runner fails closed when a required command is missing, when Python/Deno/Supabase versions do not match the frozen CI recipe, or when any test/assertion command returns non-zero.

## Qualification equivalence

The local runner reproduces the substantive commands in `.github/workflows/ci.yml` without requiring a GitHub-hosted runner:

1. Python 3.11 and 3.12 each create a clean temporary virtual environment.
2. Each installs `pip==26.2.1` and `.[test]`, runs `compileall`, the complete pytest suite, and `scripts/radar_source_hashes.py`.
3. Deno runs `deno ci` and `deno check index.ts` from `supabase/functions/github-bus-ingest` using the frozen dependency graph.
4. Local Supabase starts through Docker, rebuilds from the migration chain with `supabase db reset`, then every `supabase/tests/radar_*.sql` assertion runs with `ON_ERROR_STOP=1`.
5. Local Supabase is stopped with `--no-backup` even when SQL qualification fails after startup.

A PASS receipt is valid only for the exact Git commit reported by the runner as `source_commit`. A receipt from another commit does not qualify a successor head.

## GitHub Actions status

Private GitHub-hosted Actions may remain present as opportunistic/free-quota signal, but they are not a gating dependency and must not trigger plan, billing, payment-method, spending-limit, or other paid-service changes.

Issue #39 remains historical/infrastructure evidence for the repeated pre-runner failures. Its resolution for Radar is replacement of the paid-capable dependency with this local path, not purchase of runner capacity.

Public GitHub-hosted Actions may be used only for deliberately public, non-secret, non-sensitive verification payloads where public execution is appropriate. Do not mirror private repository source into a public repository merely to obtain free CI.

## Boundary

This operator path authorizes local verification only. It does not authorize merge, deployment, provider migration, provider configuration, cursor seeding, dispatcher activation, branch-history rewrite, billing/account changes, or any other protected/live effect.
