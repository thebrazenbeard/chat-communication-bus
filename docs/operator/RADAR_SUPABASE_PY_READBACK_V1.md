# Radar Supabase Python readback V1

Status: `SOURCE_ONLY / READ_ONLY / NO_PROTECTED_EFFECT`

Purpose: provide an independent provider data-plane readback path for Radar using the official `supabase-py` SDK. Git remains canonical. A successful SDK read proves only the provider state actually returned by that read.

## Trust-plane boundary

This reader is deliberately separate from:

- GitHub Actions OIDC issuance and the `github-bus-ingest` write path;
- Supabase migration, Edge deployment, function configuration, secrets, and gateway management;
- canonical Git source qualification and currentness.

It must not be used to infer that provider recovery completed merely because one data-plane read succeeds.

## Install

Use the optional dependency group:

```text
pip install -e ".[provider-readback]"
```

The contract pins stable `supabase-py` v2 (`supabase==2.31.0`).

## Credentials

By default the CLI reads:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

The CLI never prints either value. The service-role credential is privileged even though this wrapper is read-only; keep normal provider-secret handling in force.

Environment variable names can be overridden with `--url-env` and `--key-env`.

## Guaranteed read surface

After `20260906165117_radar_projection_journal_api_v1.sql` exists at the provider, the guaranteed PostgREST read surface is:

`public.radar_projection_get_lane_v1`

Example:

```text
python scripts/radar_supabase_readback.py lane --identity-id radar --branch bus/radar-v2
```

## Capability-only operator views

The reader also supports:

```text
python scripts/radar_supabase_readback.py messages --recipient-identity-id vera --limit 100
python scripts/radar_supabase_readback.py assignments --limit 100
```

These use `radar.identity_message_status_v2` and `radar.open_assignments_v1`. Their SQL grants exist in source, but successful PostgREST access also requires the `radar` schema to be exposed by the provider API. Treat failure as `PROVIDER_READ_FAILED`, not as proof that the underlying database objects are absent.

## Current issue #16 ceiling

This reader does not inspect the Supabase migration ledger or Edge-function metadata. Those remain management-plane readbacks. Therefore it cannot by itself prove:

- all six missing Radar migrations were applied;
- `github-bus-ingest` was replaced with the qualified successor;
- `verify_jwt` changed from the live legacy value;
- `RADAR_TRUSTED_PROJECTOR_SHA` is correct;
- projection cursors were deliberately bootstrapped;
- the complete Git -> OIDC -> Edge -> atomic projection route recovered.

Use it as an independent data-plane verifier inside that larger recovery sequence, not as a replacement for the sequence.
