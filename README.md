# Radar / Chat Communication Bus

Radar is the owner/operator control plane for `thebrazenbeard/chat-communication-bus`. GitHub `main` and the current contracts are canonical; writer lanes are durable append-only mailboxes/provenance. Supabase is a rebuildable projection/runtime, not canonical history.

Patrick is the human override authority. Protected effects—provider migrations/deployments/configuration, cursor bootstrap, repository rules/settings, merge/cutover effects, credentials, and history rewriting—remain separately gated.

## Current routing and source

Read these first:

- `architecture/contracts/RADAR_CURRENT.json` — present-tense source/provider status.
- `architecture/contracts/RADAR_TOPOLOGY_V1.json` — current writer-lane lifecycle/routing authority.
- `architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json` — source classes/files that must remain hash-custodied.
- `docs/protocol/PROTOCOL_V2.md` and `docs/protocol/BUS_MESSAGE_GRAMMAR_V1.json` — protocol/message grammar.
- `docs/operator/RECOVERY.md` — recovery procedure.
- `architecture/contracts/RADAR_SUPABASE_V1.md` — provider realization and drift.

Radar's current mailbox is `bus/radar-v2`. Historical `bus/radar-v1` and `radar/control-plane-v1` remain provenance only. Current topology marks only lifecycle `ACTIVE` lanes as routing/reconciliation authority; Parallax is presently `REGISTERED_INERT / FIRST_APPEND_PENDING` and is not routable.

## Current hardening line

The reviewed source hardening implements/defines:

- canonical shared message grammar and strict writer admission;
- exact node-level routing with leases and node-bound subscriptions;
- priority/dedupe/heartbeat semantics required by Radar V1;
- atomic legacy Slack relay state transitions without restoring Slack as active transport;
- durable fenced projection cursors/batches/files;
- central trusted reconciliation where writer branches are inert Git objects;
- exact-body-bound GitHub OIDC with one-time JTI consumption before semantic parsing;
- immutable trusted-projector source anchors and default-branch dispatcher source;
- ordered migration provenance, real SQL CI source, exact tool pins, and manifest-driven source custody.

Some of that source is still in stacked Draft PRs and is not provider/runtime state. `RADAR_CURRENT.json` is authoritative for that distinction.

## Provider status

Fresh 2026-09-06 readback shows the Supabase Radar ledger applied only through `20260903113314_radar_operator_views_v1`. Five later Radar source migrations are unapplied, including replay guard, node routing hardening, and projection journal/API migrations. The live `github-bus-ingest` Edge function remains version 3 with `verify_jwt=true`; the body-bound central GitHub OIDC source and projection anchor B are not deployed/configured. Provider projection is therefore `PARTIAL_NOT_CURRENT` relative to Git source.

Do not infer authorization from that drift report. Recovery/deployment sequence is documented in `docs/operator/RECOVERY.md`.

## Verification

Source CI is designed to run Python 3.11/3.12, source custody, frozen Deno Edge type checking, clean local Supabase migration reset, and every `supabase/tests/radar_*.sql` assertion. Recent hosted GitHub Actions jobs have been terminating before runner assignment (`runner_id: 0`, zero steps), so source units affected by that outage are not represented as fully GREEN until executable verification succeeds.

Current Task-10 source also deliberately requires a Deno-generated `supabase/functions/github-bus-ingest/deno.lock`; it must not be fabricated by hand.

## Historical receipts

Phase 18/19, dated cutover documents, old migration/Realtime receipts, and predecessor branch records remain useful historical evidence at their original scope. They are not present-tense topology/provider authority. In particular, dated writer-lane cutover snapshots must never be replayed as current topology during recovery.

No writer-lane history should be rebased, force-pushed, squashed, deleted, or rewritten by Radar maintenance.
