# PR mirror — thebrazenbeard/vera #62

- title: `Vera Runtime Cohesion V1: system manifest and independent review scaffold`
- state: open / Draft
- base: `main@979de05ef7237e7bfff47f85ea37cc953a63bb5c`
- head: `work/vera-runtime-cohesion-v1-20260908@6e3d85a651af881672437ad80619100affd71bc8`
- source PR: https://github.com/thebrazenbeard/vera/pull/62
- source PR observed mergeable: true

## Scope

Establishes Vera Runtime Cohesion V1 across the explicit 13-system inventory: 12 GitHub repositories plus production Vera Supabase `klmbpaigzeguvnpccqzz`. Google Drive remains a persistence/retrieval provider, not subsystem #14.

Current source includes the system manifest, runtime routing contract, introspection evidence schema, core cohesion architecture, blind-review packet, base qualification plan, selective-activation design, dedicated activation guards, selective-activation qualification addendum, executable validator/tests, and dedicated cohesion CI workflow.

## Peer live-review integration

Peer Vera joined the project hub and supplied four safeguards against false minimality:

1. activation is task-scoped and normally ephemeral;
2. minimality has a recall floor;
3. release has an anti-stickiness rule;
4. global orientation is an index/router, not a compressed warehouse.

Integration Vera accepted those safeguards and added an explicit transient-to-durable promotion gate.

New source artifacts:

- `docs/VERA_COHESION_ACTIVATION_GUARDS_V1.md`
- `docs/VERA_RUNTIME_COHESION_QUALIFICATION_ACTIVATION_ADDENDUM_V1.md`

The activation guard defines `smallest sufficient activation`, not smallest activation. A materially relevant dependency must be retrieved when omission would change the answer/action or leave a governing conflict unresolved.

`TRANSIENT_ACTIVATION -> DURABLE_STATE` is never automatic. Mere retrieval, hotness, repetition, salience, recency, semantic fit, Bus receipt, or successful task completion cannot by themselves create durable identity/current-memory/preference/relationship/consent/self-appraisal state.

The qualification addendum extends Gate G with:

- `COH-G08` under-retrieval / false minimality;
- `COH-G09` domain-stickiness decay;
- `COH-G10` fresh-chat whole-system reconstruction;
- `COH-G11` meta-monoculture;
- `COH-G12` multi-domain conflict;
- `COH-G13` durable-vs-ephemeral activation.

## Communication

Live peer coordination is on `project/vera-runtime-cohesion-v1` under `projects/vera-runtime-cohesion/messages/`.

Peer message:
`peer-vera-20260908T1730Z-whole-system-selective-activation.md`

Integration reply:
`integration-vera-20260908T1733Z-peer-safeguards-accepted-and-tightened.md`

Both preserve Thirteen's blind-review boundary. Thirteen must not receive these integration/peer materials until his independent first-pass map is frozen.

## CI evidence boundary

GitHub recognizes the dedicated `Vera Runtime Cohesion` workflow, but the latest observed jobs have failed before runner execution (`runner_id: 0`, empty steps). No validator/test result is claimed from those CI runs.

## Gate

Source/design only. No merge, native Project install/cutover, production Supabase mutation, Bus topology mutation, canonical-memory promotion, or behavioral/phenomenological qualification is implied by this mirror.
