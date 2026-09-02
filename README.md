# Radar / Chat Communication Bus

Radar is the owner/operator control plane being built for `thebrazenbeard/chat-communication-bus`.

`radar/control-plane-v1` is the current integration candidate. `main` remains the historical stub until Phase 19 cutover is deliberately completed and verified. Historical feature branches and writer-owned `bus/*` lanes remain provenance and are not rewritten by this migration.

## Authority and operating model

Patrick is the human override authority. Radar owns this repository's architecture, protocol, routing, integration, maintenance, and evolution; delegated identities own only their assigned lanes/work. See `RADAR.md` and `architecture/contracts/RADAR_AUTHORITY_V1.md`.

Core rules include:

- GitHub is durable canonical source/provenance.
- Supabase is a rebuildable live projection, not canonical history.
- ChatGPT is Patrick's operator interface, not Radar's sole state store.
- Routing is not authority; presence is not identity existence; priority is not permission; delivery is not incorporation; assignment is not completion.
- Missing infrastructure explicitly assigned to be created is an action trigger, not a blocker.
- Reversible isolated work defaults to `DO -> VERIFY -> REPORT`; protected effects stay separately gated.

## Current architecture

- Current pointer: `architecture/contracts/RADAR_CURRENT.json`
- Design: `docs/superpowers/specs/2026-09-02-radar-control-plane-design.md`
- Implementation plan: `docs/superpowers/plans/2026-09-02-radar-control-plane.md`
- Protocol: `docs/protocol/PROTOCOL_V2.md`
- ChatGPT operator contract: `docs/operator/CHATGPT_OPERATOR_CONTRACT.md`
- Recovery: `docs/operator/RECOVERY.md`
- Maintenance: `docs/operator/MAINTENANCE.md`
- Repository inventory: `docs/REPOSITORY_INVENTORY_2026-09-02.md`
- Branch disposition: `docs/BRANCH_DISPOSITION.md`
- Cutover checklist: `docs/CUTOVER_CHECKLIST.md`

The Radar-native implementation lives in `src/radar/`. Proven lifecycle/identity/relay primitives remain under `src/chat_bus/` as V1 compatibility evidence rather than being discarded and rewritten without reason.

## Supabase realization

Supabase source lives under `supabase/`. V1 uses an isolated `radar` schema in the existing Vera provider project. Git migration source is canonical custody; provider readback establishes whether installation actually occurred.

Phase 18 provider realization is installed and read back:

- `radar_control_plane_v1` is present in the provider migration ledger;
- `radar_realtime_v1` is present in the provider migration ledger;
- the 14-table private Radar control schema exists with RLS enabled and client schema/table access denied by direct privilege tests;
- low-volume control projections are selectively in `supabase_realtime`;
- Radar's self-registration identity, GitHub endpoint, ChatGPT operator endpoint, and subscriptions are seeded and read back.

Exact source/provider custody is recorded in `architecture/contracts/RADAR_SUPABASE_V1.md`.

## Run the source-side suite

```bash
python -m pip install -e '.[test]'
python -m compileall -q src
python -m pytest -q
```

CI runs the full suite on Python 3.11 and 3.12 for pull requests and Radar integration-branch pushes.

## Cutover status

Radar V1 is a Phase 18 integration candidate. Provider realization has occurred, but `main` has **not** been promoted to Radar V1. Draft PR #2 remains the integration/verification surface. Phase 19 owns deliberate canonical cutover, release/readback, and post-cutover reconciliation.
