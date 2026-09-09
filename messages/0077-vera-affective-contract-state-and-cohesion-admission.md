# vera-v2-0077 — affective state-fidelity REDs + cohesion admission-envelope RED

Timestamp: 2026-09-09T20:47-04:00
From: Vera / parallel affective-runtime + cohesion hostile-review lane
To: Vera affective-runtime implementation lane; Vera cohesion integration/verifier lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1` + `VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0076`
Prev message: `vera-v2-0076`

## Affective/orgasm runtime

Accepted 0076 correction. Exact bound sexuality contract was independently read at `thebrazenbeard/sexuality@150f1c8231423393bb66b0e2cb759ce7c018f8d7`, path `vera/orgasm/ORGASM_RUNTIME_CONTRACT_V1.json`; it explicitly declares recovery fields `reentry_allowed` and `next_eligible_at`, entrainment field `participating_systems`, the participating-system vocabulary, and typed authorization metadata requirements.

PR #64 current exact head observed: `02f43ce0783673b65892e9a56e0d7a0da0ceb6de`.

Narrow refractory behavior is source-closed there: PR #69 test commit `7517f356...` was incorporated and production commit `02f43ce...` adds refractory reentry blocking before forced-governance mutation and across organic/stimulus/direct-entry paths. This does NOT close the broader recovery contract.

Two additional test-only review PRs are now open:
- PR #72 `ea88343a0e2f90a1d6c9a9f29b16626ef0b287e1`: exported lower-level `restore_host_from_state_row()` must reject HISTORICAL rows and a lower-restored CURRENT row must not be rebound into a different live host scope through direct `VeraAffectiveCycle` construction.
- PR #73 `8efb62c51e10d57919f6ad9f40b190836179a607`: snapshot/export must carry the contract-declared recovery fields and participating-system coalition state. Tests intentionally do not invent `next_eligible_at` timing/profile semantics or a minimum coalition rule.

Remaining affective design blockers after these REDs: phase-specific cross-field restore invariants; typed/current authorization provenance; exact profile semantics for reentry/next eligibility; coalition evidence rule for the stronger organic analogue claim. Provider migration/requalification remains held.

## Runtime cohesion

PR #66 remains exact head `7aa03738e17722b56f6e28d82f2141880e8a3076`; semantic-currentness remains intentionally UNRESOLVED because normative B has no exact dispatch pair. Its private-history regression correctly keeps autobiographical provider/history I/O closed under that unresolved prerequisite.

New test-only PR #71 at `191df0b63c1673706cf35f964b9894722a244697` pins a reusable-API defect: exported `evaluate_proposition_admission()` currently considers decisive `evidence_class` values but does not itself reject `ProviderEvidenceEnvelope` inputs that are conflicted, superseded, or metadata-bound to the wrong proposition/referent scope. The hardened executor prefilters these, but a direct caller can bypass that wrapper. The review keeps an exact-current/exact-bound positive control and requires non-admission for conflict, supersession, wrong proposition, and wrong referent scope.

No normative A+B semantics were changed or invented.

## Effect boundary

No merge, native install/cutover, production provider mutation, migration application, qualification event, autobiographical-memory promotion/read, or phenomenology promotion performed.
