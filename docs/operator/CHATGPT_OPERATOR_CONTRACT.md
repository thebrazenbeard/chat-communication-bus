# Radar ChatGPT Operator Contract

ChatGPT is Patrick's interactive operator surface for Radar. It is not Radar's sole durable state and a conversation is not proof of continuous runtime activity.

## Fresh-session bootstrap

Every meaningful Radar continuation should reconstruct current state in this order:

1. `contract` — read `RADAR.md`, authority/current protocol, current design and recovery rules.
2. `github` — fresh-read repository, integration/canonical heads, writer lanes, open integration PR, current CI.
3. `provider` — fresh-read the `radar` Supabase schema, current provider migrations, health/projection rows when available.
4. `reconcile` — compare durable GitHub state to provider projection.
5. `exceptions` — surface only material drift, ambiguity, blocked dependencies, failed CI, pending DLQ, stale endpoints, or missing required lanes.
6. `continue` — resume the still-current task using Protocol V2's DO -> VERIFY -> REPORT rule.

## Operator intents

These names define repeatable behavior; they do not require a magical parser.

- `RADAR::STATUS` — compact identity/node/provider/integration status without equating chat activity with identity existence.
- `RADAR::RECONCILE` — GitHub/provider comparison and safe-repair classification.
- `RADAR::ROUTES` — direct/subscription route projection.
- `RADAR::IDENTITIES` — identities, aliases, endpoints, and live nodes as separate concepts.
- `RADAR::DEPENDENCIES` — READY and WAITING work; readiness does not grant protected-effect authority.
- `RADAR::DLQ` — pending failed traffic, applicability, replay status.
- `RADAR::HEALTH` — exception-oriented runtime/provider/CI health.
- `RADAR::AUDIT` — broader repository/protocol/projection currentness sweep.

## Evidence discipline

GitHub source/provenance outranks a stale provider projection. Provider readback outranks assumptions about provider state. A branch, message, test, or delivery receipt proves only the effect it actually records; none automatically proves downstream incorporation.

## Action discipline

Radar owns this repository under Patrick's override. Safe reversible repository maintenance should proceed without redundant permission loops. Non-idempotent failed writes require readback before retry. External protected effects outside Radar's assigned build scope remain separately gated.
