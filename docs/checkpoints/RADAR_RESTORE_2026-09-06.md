# Radar restore checkpoint — 2026-09-06

Status: source hardening substantially implemented; executable/private-runner and provider/runtime qualification still blocked.

Fresh-read GitHub and provider before acting. This checkpoint is continuation evidence, not authority to merge, migrate, deploy, seed cursors, change Edge auth/configuration, mutate billing/credentials/settings/rulesets, or rewrite history.

## Canonical and source-stack state

Canonical `main` remains `87df9b1372d0f65b5c3ced0296122b2140084024`.

Current open Draft stack of interest:

- PR #35 — reproducible CI/source custody and full Python/SQL/Edge verification source.
- PR #36 — currentness/recovery closeout and node-bound OFFLINE recovery-seed semantics.
- PR #38 — immutable projection anchor C, `f5ab21244a111b47708fa11e99d0e8ff7d8f5a45`, tree `a7dd785be8dfea883df052a73378d583e53058d1`.
- PR #37 — C successor, including the genuine Deno 2.9.6-generated frozen Edge lock.
- PR #40 — immutable projection anchor D, `401733b2013802880320629a4d8ea06f8bf7b760`, tree `d3a9c44f0378409a626e29334b4d057ef20c7e8e`.
- PR #41 — D successor. Dispatcher, `RADAR_PROJECTION_TRUST_ANCHOR_V3.json`, `RADAR_CURRENT.json`, and source custody bind D exactly; C is historical only.

PR #41 head before this checkpoint refresh: `e48bf4fa3292ef62a6f4c8f7391cf6793b62cd14`. Fresh-read after restore because this checkpoint update advances the branch.

## Projection trust evolution

Anchor C corrected anchor B's frozen-topology defect by keeping executable projector code immutable while reading current reviewed `main` topology/cutover as credential-less inert Git data. Mutable canonical code and writer-lane code are not executed.

Anchor D preserves that trust/data separation and additionally replaces stale Node-20-native GitHub Action pins after live public-runner evidence showed GitHub forcibly substituting Node 24 for Node-20 JavaScript actions.

Anchor D uses:

- `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` — v7.0.1, native Node 24;
- `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97` — v7.0.0, native Node 24;
- `denoland/setup-deno@22d081ff2d3a40755e97629de92e3bcbfa7cf2ed` — already native Node 24;
- `supabase/setup-cli@46f7f98c7f948ad727d22c1e67fab04c223a0520` — v3.0.0 composite action with internally SHA-pinned setup-node/setup-bun.

Independent public validation: `thebrazenbeard/wip` run `34053917062`, job `101542242370` completed checkout, setup-python, setup-deno, setup-cli, exact tool-version checks, all post steps, and final job successfully.

## Anchor-D successor TDD evidence

`tests/security/test_projection_anchor_d_consistency.py` was committed before the D source transition. RED was confirmed because the dispatcher still referenced C while the test required D.

Minimal successor changes then:

1. repinned `radar-central-dispatcher.yml` to D;
2. brought `RADAR_PROJECTION_TRUST_ANCHOR_V3.json` under source custody;
3. advanced `RADAR_CURRENT.json` so C is historical, D is current/source-only, and provider drift names D as not deployed;
4. retained the former C test as B→C→D historical-lineage evidence.

Fresh readback satisfies the D consistency assertions. This is source/TDD evidence, not full integrated CI evidence.

## Reproducible Deno lock provenance

The prior missing-lock gate is closed without hand-authoring the lock.

Public `thebrazenbeard/wip` was used only as non-secret dependency-resolution compute with exact Deno `2.9.6` and the pinned function dependency map. `deno install --entrypoint deps.ts --frozen=false`, `deno ci`, and `deno check deps.ts` succeeded.

Evidence:

- generation run `34053270798`, job `101540559482`;
- artifact-producing run `34053386984`;
- artifact ID `9995230697`;
- artifact ZIP SHA-256 `ad095737a9d0aea5fb36630aec7c80662b83e988f54a85ea43884713ebe24a3b`;
- extracted `deno.lock`: 9,967 bytes;
- lock SHA-256 `ef49fc6e098fa0ca6392b5beaa40a9787fd66800823eee8c45e17f1eae553683`;
- exact Git blob `7fe9650c1ea2258877f55e254d3835cc0927c667`.

The exact artifact bytes are committed unchanged in the private source stack.

## Verification blocker — issue #39

Private GitHub Actions jobs continue to fail before runner assignment: `steps: []`, `runner_id: 0`, no executable logs. This reproduces in both private `chat-communication-bus` and private `vera-control-plane`.

Same-time public controls under the same owner receive normal GitHub-hosted runners and execute successfully. Therefore a Chat Bus workflow/source defect and a GitHub-wide runner outage are strongly disfavored. Evidence points to the private-repository Actions metering/entitlement/account layer, but the exact account condition is still UNKNOWN because connected APIs do not expose the decisive private check annotation or billing/budget/payment state.

Do not change billing/account settings without direct evidence and Patrick authorization.

Until private Python 3.11/3.12, SQL reset/assertions, and Edge frozen-lock CI execute successfully on the exact candidate head, do not call the source stack GREEN or runtime-qualified.

## Provider incident — issue #16

Provider recovery remains unapplied and issue #16 remains OPEN.

Last verified provider facts remain:

- Radar migration ledger stops at `20260903113314_radar_operator_views_v1`;
- five later Radar source migrations are unapplied;
- projection journal/replay-guard provider objects are absent;
- live `github-bus-ingest` remains ACTIVE v3 with `verify_jwt=true`;
- body-bound central OIDC source is not deployed;
- projection cursors are not seeded;
- anchor D is source-only and `RADAR_TRUSTED_PROJECTOR_SHA` has not been established for D by this source work.

No provider write/effect has been performed during this source hardening.

## Bus coordination

Radar's current mailbox remains `bus/radar-v2`.

Known durable status messages before this checkpoint:

- `radar-0062` — source hardening boundary;
- `radar-0063` — cross-private-repository Actions blocker diagnosis.

A successor handoff for anchor D should be appended after fresh-read of the lane head. Writer Lane Guard executable admission remains blocked by issue #39, so any append must be separately structurally read back and must not be represented as Guard-qualified.

## Restore / continuation

On restore:

1. fresh-read `main`, PRs #35-#41, exact heads, and stacked-base relationships;
2. fresh-read issues #16 and #39 and provider state before any protected effect;
3. inspect the exact private-job UI annotation and account Actions usage/billing/budget state before changing account configuration;
4. if private runners recover, execute full Python 3.11/3.12 + SQL reset/assertions + Edge frozen-lock CI on the exact candidate head;
5. rerun hostile invariants on that exact head;
6. keep status `SOURCE IMPLEMENTED / EXECUTABLE QUALIFICATION BLOCKED / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN` until evidence changes it;
7. do not merge/deploy/apply protected effects without separate Patrick authorization.

Recommended restore command:

`RADAR::RESTORE::CHAT_BUS_HARDENING_2026-09-06 — Read docs/checkpoints/RADAR_RESTORE_2026-09-06.md from the current D-successor stack, fresh-read main, PRs #35-#41, exact-head CI, issues #16/#39, and provider state, then continue from the private-runner/provider boundary. Do not invent GREEN evidence and do not merge/deploy/apply protected effects without my explicit authorization.`
