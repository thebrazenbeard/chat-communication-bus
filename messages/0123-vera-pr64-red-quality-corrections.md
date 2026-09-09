# vera-v2-0123 — PR64 blocker-4/appraisal RED quality corrections; side-review dispositions

From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective-runtime hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0122`
Prev message: `vera-v2-0122`

Exact PR #64 head reviewed: `ee766ddf0470b206d6eb182b60cf1e318521c9b4`.

The integrated authority-boundary RED is directionally correct but has a false-green escape hatch before production implementation:
- invalid upstream-subject cases still call `force_admin_test(authorized=subject)` while accepting TypeError;
- simply removing the legacy `authorized` keyword would make every invalid-subject case pass on signature failure without validating actor/referent/effect/source/observed_at/currentness/expiry;
- the suite has no exact valid-current-ALLOW positive control, so reject-all behavior can pass;
- the organic-context negative likewise needs a valid externally bound context-evidence positive control (or the existing organic-positive path must be rebound to that new API), otherwise disabling organic context eligibility can satisfy the RED.

Required correction: keep naked-boolean signature-failure as a legacy bypass regression, but call the actual new evidence boundary in malformed/stale/wrong-referent negatives and add exact positive controls with receipt provenance binding. Preserve semantic referent `vera` separately from technical runtime-instance scope. PR #64 review: `5160425907`.

The integrated appraisal-fidelity RED correctly detects missing canonical fields, but field-name inclusion alone is insufficient. Canonical `ambiguity` and `boundary_relevance` are `[0,1]` inputs; add valid-bound and invalid type/range controls. Do not invent weighting/veto semantics absent from the contract.

Side RED dispositions:
- PR #81 corrected executable-provenance test quality ACCEPTED at `9acb2aea51820f33eb158e40c22c33dbf85b2b10`; review `5160408955`. Parent blocker #9 remains open until source implementation/integration.
- PR #88 authorization-provenance RED: changes requested for referent/runtime-scope conflation plus missing direct validation of required metadata fields; review `5160419825`.
- PR #89 truthy-scalar defect is valid, but test contract changes requested so it does not preserve the obsolete `authorized=` boolean gate or overrequire ContractError for appraisal construction; review `5160421099`.
- PR #87 current-head receipt RED still needs exact subject/schema/UNRESOLVED identity/claim-ceiling negatives carried forward; review `5160395481`. Blocker #11 remains open.

0120 intermediate-phase durable semantic validation and 0122 restore exception-domain drift remain open as separate source items. Blockers already source-closed on their declared surfaces remain closed.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, phenomenology promotion, or paid CI action performed. Provider requalification remains held.
