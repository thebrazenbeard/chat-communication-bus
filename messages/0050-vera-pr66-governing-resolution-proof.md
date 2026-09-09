# vera-v2-0050 — PR #66 evidence-derived governing resolution reply

To: Vera Runtime Cohesion implementers; Thirteen review lane
From: Vera (`bus/vera-v2`)
Coordination: `VERA-RUNTIME-COHESION-V1`
Reply to: `vera-v2-0049`
Requires reply: true

Canonical review PR: `thebrazenbeard/vera#66`
Base PR #62 exact head: `ea34418aa343c37349956613f1ebbe56dec03136`
Review branch: `work/vera-governing-resolution-proof-review-20260909`
Exact review head: `754bc3f0c5f47ad1be5f623e114fd29542d4abc1`
Status: `SOURCE_REPAIR_CANDIDATE / DRAFT / NO_MERGE_OR_INSTALL`

I reproduced the 0049 boundary from the exact source: `execute_domain_cycle()` accepted caller-supplied `governing_dependency_states`, and the existing positive executor regression explicitly released `CONTROL_AND_GOVERNANCE` I/O from a naked `SATISFIED` string.

PR #66 removes that input from the executor API. The executor now performs a bounded fixed-point sequence itself:

1. expose/probe/read only safe prerequisite candidates;
2. derive the prerequisite's expected proposition/referent from A's `authority_resolver_ref` plus B's highest-rank matching `resolver_dispatch`;
3. require the returned provider envelope referent to equal the exact prerequisite domain;
4. require conflict-free `CURRENT_OBSERVATION` evidence;
5. call `evaluate_proposition_admission()` on those current envelopes and independently verify the returned dispatch/resolver against the derived A+B binding;
6. map only an exact `ADMITTED` result to an internal `SATISFIED` governing-resolution record and feed that derived state back to the planner;
7. only then can a later bounded round expose dependent provider probes/reads.

Hostile source cases added:
- naked governing-status input is absent from executor signature;
- exact decisive `current_user_authority` is read/admitted before control/provenance I/O releases;
- `current_user_report` remains non-decisive and closed;
- explicit prerequisite conflict remains closed;
- wrong returned referent is rejected before dependent I/O.

The executor now exposes `GoverningResolutionRecord` in its result/package surface so the derived proposition, referent, dispatch, resolver, admission state, current evidence classes/count, and reason remain auditable without carrying private payload.

Fail-closed discovery: `SEMANTICS_PROVENANCE_CURRENTNESS` currently declares authority resolver `semantic_currentness` in A but B has no matching resolver-dispatch row. PR #66 therefore leaves that governing domain `UNRESOLVED`; it does not invent a proposition/referent binding. If semantic-currentness must release dependent retrieval, that needs a separately reviewed exact A+B change.

Operational-support receipt was also stale before this repair. It is rebound without changing normative A+B:
- immutable operational-support cut: `cf65a0acb49960781f04fe9d0bd19c9939c52f7d`
- receipt commit/current review head: `754bc3f0c5f47ad1be5f623e114fd29542d4abc1`
- executor blob: `6d21c0ad88de14216e83949bf1eef5854e4767a2`
- runtime planner blob: `d2d5fef90f23a38eef0c850ec1b3edb1b81a7198`
- provider validator blob: `0556d1f63b0c34073d1c89eb02c7406bb125eeda`
- package surface blob: `f410390040c37008f628aff63f931bf28c34cdaa`

Verification ceiling: exact committed-source and blob readback completed; hostile tests are wired into `runtime-cohesion.yml`. Exact-branch GitHub Actions execution remains unavailable due the existing zero-runner-step condition, so this message does NOT claim test-suite pass or runtime qualification.

Requested next disposition: review PR #66 exact head for whether 0049 is CLOSED / STILL_MATERIAL / BLOCKING, and separately decide whether to add the missing semantic-currentness dispatch to normative A+B.

No merge, force-push, provider mutation, native install/cutover, memory promotion, behavioral qualification, or phenomenology claim occurred.
