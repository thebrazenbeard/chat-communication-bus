# Radar Maintenance

Radar maintenance is exception-oriented. Routine healthy state should not produce ceremony or permission loops.

## Checks

At an audit/reconciliation pass inspect:

- required identity lanes vs observed lanes;
- logical identity aliases and duplicate writer claims;
- stale endpoints/nodes without treating node offline as identity deletion;
- pending DLQ items and applicability;
- stuck or newly satisfied dependencies;
- stale acknowledgements;
- Protocol/current-pointer drift;
- GitHub/provider projection mismatch;
- current PR/head CI status;
- stale architecture/operator/recovery docs;
- orphaned provider identities/endpoints;
- provider migration/source custody;
- unintended anon/authenticated Radar privileges;
- selective Realtime publication membership.

## Response classes

`SAFE_PROJECTION_REPAIR` — GitHub durable state is unambiguous and provider projection can be repaired without changing durable source authority.

`AMBIGUOUS_DURABLE_CONFLICT` — competing durable writer/currentness claims exist; preserve evidence and resolve deliberately.

`OBSERVATION_ONLY` — noteworthy but not an actionable defect.

## Cadence

Run maintenance after material repository/provider changes, during fresh Radar bootstrap, before Phase 19 cutover, and when symptoms suggest drift. Do not generate periodic noise merely to prove Radar is alive.

## Automatic-safe examples

- project a known writer lane into missing provider projection;
- mark an expired live node OFFLINE;
- refresh protocol-head projection from an unambiguous Git current pointer;
- surface newly satisfied dependency as READY.

## Not automatic

- choosing between two competing durable writer claims;
- force-moving/deleting history;
- interpreting message delivery as incorporation;
- converting priority into authority;
- broadening a narrow task assignment into unrelated protected effects.
