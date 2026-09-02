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

- Design: `docs/superpowers/specs/2026-09-02-radar-control-plane-design.md`
- Implementation plan: `docs/superpowers/plans/2026-09-02-radar-control-plane.md`
- Protocol: `docs/protocol/PROTOCOL_V2.md`
- ChatGPT operator contract: `docs/operator/CHATGPT_OPERATOR_CONTRACT.md`
- Repository inventory: `docs/REPOSITORY_INVENTORY_2026-09-02.md`
- Branch disposition: `docs/BRANCH_DISPOSITION.md`
- Cutover checklist: `docs/CUTOVER_CHECKLIST.md`

The Radar-native implementation lives in `src/radar/`. Proven lifecycle/identity/relay primitives remain under `src/chat_bus/` as V1 compatibility evidence rather than being discarded and rewritten without reason.

Supabase source lives under `supabase/`. The V1 design uses an isolated `radar` schema in the existing provider project; Git migration source is authoritative for what should be installed, while provider readback is authoritative for whether installation actually occurred.

## Run the source-side suite

```bash
python -m pip install -e '.[test]'
python -m compileall -q src
python -m pytest -q
```

CI runs the full suite on Python 3.11 and 3.12 for pull requests and Radar integration-branch pushes.

## Cutover status

Radar V1 is still an integration candidate, not yet a claim that `main` or the live Supabase provider has been cut over. Draft PR #2 is the integration/verification surface. Phase 19 owns release/cutover/recovery operationalization after the Phase 1-18 readiness gates are satisfied.
