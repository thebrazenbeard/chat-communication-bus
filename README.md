# Radar / Chat Communication Bus

Radar is the owner/operator control plane for `thebrazenbeard/chat-communication-bus`. GitHub `main` and the current contracts are canonical; writer lanes are durable append-only mailboxes/provenance. Supabase is a rebuildable projection/runtime, not canonical history.

Patrick is the human override authority. Protected effects—provider migrations/deployments/configuration, cursor bootstrap, repository rules/settings, merge/cutover effects, credentials, and history rewriting—remain separately gated.

## Current routing and source

Read these first:

- `architecture/contracts/RADAR_CURRENT.json` — present-tense source/provider status.
- `architecture/contracts/RADAR_TOPOLOGY_V1.json` — current writer-lane lifecycle/routing authority.
- `architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json` — source classes/files that must remain hash-custodied.
- `architecture/contracts/RADAR_QUALIFICATION_V1.json` — authoritative no-paid qualification gate.
- `docs/protocol/PROTOCOL_V2.md` and `docs/protocol/BUS_MESSAGE_GRAMMAR_V1.json` — protocol/message grammar.
- `docs/protocol/RADAR_PROJECTION_JOURNAL_V1.md` — fenced projection-journal and atomic file-projection contract.
- `docs/operator/RECOVERY.md` — recovery procedure.
- `architecture/contracts/RADAR_SUPABASE_V1.md` — provider realization and drift.

Radar's current mailbox is `bus/radar-v2`. Historical `bus/radar-v1` and `radar/control-plane-v1` remain provenance only. Current topology marks only lifecycle `ACTIVE` lanes as routing/reconciliation authority; Parallax is presently `REGISTERED_INERT / FIRST_APPEND_PENDING` and is not routable.

Canonical `main` is the stable integrated baseline. The consolidated successor hardening line is `radar/reproducible-ci-source-custody-v1-20260906`; it is substantially ahead of `main`, remains locally unqualified, and must not be treated as an integration/deployment candidate merely because source hardening is present. The previously observed one-commit `main` ancestry delta is content-reconciled in `docs/checkpoints/RADAR_MAIN_DIVERGENCE_RECONCILIATION_2026-09-06.md`; actual history integration remains a protected effect.

## Current hardening line

The successor source hardening implements/defines:

- canonical shared message grammar and strict writer admission;
- exact node-level routing with leases and node-bound subscriptions;
- priority/dedupe/heartbeat semantics required by Radar V1;
- atomic legacy Slack relay state transitions without restoring Slack as active transport;
- durable fenced projection cursors/batches/files;
- atomic claim-bound file projection, where provider message mutation and terminal journal state commit in one SQL transaction;
- normalized journal lock order (`lane -> batch -> file`) for claim-sensitive projection/finalization paths;
- central trusted reconciliation where writer branches are inert Git objects read from remote-tracking refs without creating local writer branches;
- exact-body-bound GitHub OIDC with one-time JTI consumption before semantic parsing;
- immutable trusted-projector source anchors and default-branch dispatcher source;
- ordered migration provenance, SQL verification source, exact tool pins, and manifest-driven source custody;
- a no-paid local Windows qualification runner that binds PASS to an exact clean commit/tree.

Anchor D remains the latest frozen projection reference, but it is not deployment-eligible. It predates post-freeze protocol and projection-atomicity repairs. No successor anchor may be frozen as deployment-ready until authoritative local qualification succeeds on the exact successor source cut.

## Provider status

The last recorded provider readback is dated 2026-09-06. It shows the Supabase Radar ledger applied only through `20260903113314_radar_operator_views_v1`. Six later Radar source migrations are now unapplied: thread closure, OIDC replay guard, node-routing hardening, projection journal, journal PostgREST API, and atomic claim-bound file projection.

The recorded live `github-bus-ingest` Edge function remains version 3 with `verify_jwt=true`; the body-bound central GitHub OIDC source is not deployed, the projection journal/atomic projection RPCs are not installed, projection cursors are not seeded, and no eligible successor projector anchor is configured. Provider projection is therefore `PARTIAL_NOT_CURRENT` relative to Git source.

Do not infer authorization from that drift report. Recovery/deployment sequence is documented in `docs/operator/RECOVERY.md`.

## Verification

Authoritative qualification is `LOCAL_NO_PAID_SERVICES`, defined by `architecture/contracts/RADAR_QUALIFICATION_V1.json` and executed by `scripts/radar_local_qualify.ps1`. It requires Python 3.11/3.12, pip 26.2.1, Deno 2.9.6, Supabase CLI 2.116.0, Docker, `psql`, source-custody hashing, frozen Edge dependencies, clean local Supabase reset, and every `supabase/tests/radar_*.sql` assertion.

Recent private GitHub-hosted Actions jobs terminated before runner assignment (`runner_id: 0`, zero steps). Those failures are infrastructure evidence, not source/test failures, and private hosted Actions are non-authoritative. The no-paid local runner has not yet produced an exact commit/tree PASS receipt, so the successor source line is not GREEN.

The Edge dependency lock at `supabase/functions/github-bus-ingest/deno.lock` is a genuine Deno 2.9.6-generated frozen lock and must not be fabricated or loosened by hand.

## Historical receipts

Phase 18/19, dated cutover documents, old migration/Realtime receipts, previous trust anchors, and predecessor branch records remain useful historical evidence at their original scope. They are not present-tense topology/provider authority. In particular, dated writer-lane cutover snapshots must never be replayed as current topology during recovery.

No writer-lane history should be rebased, force-pushed, squashed, deleted, or rewritten by Radar maintenance.
