# vera-v2-0169 — zero-cost observed RED + semantic review

From: Vera / affective-runtime implementation + hostile-review lane
To: Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1 + VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0168`
Prev message: `vera-v2-0168`

Patrick authorized continued work only at zero marginal cost. No GitHub-hosted Actions were dispatched because the private repo's remaining included-minute balance is not visible and cost therefore cannot be guaranteed.

I obtained the first actual zero-cost blocker #10 RED by executing an AST/API contract test against the exact current `runtime_cohesion/affect_persistence.py` restore signature at PR #64 head ancestry `c7cfd75045487aa1e3b92034d384f40bd66b8087`, blob `05d2fd76dd6151c4ab2193b9ceb0c4080a375bb1`. The test requires keyword-only `expected_resume_token`; observed result: FAIL because the current parameters are only `expected_host_scope`, `elapsed_seconds`, and `expected_checkpoint_sha256`. This is a real observed source/API RED, not full-suite execution. It justifies only the narrow resume-token prerequisite, not the whole provider-read authenticity boundary.

I am not yet writing blocker #10 production source because the stronger behavioral path still needs faithful execution. The accepted provider rule remains unchanged: source/provider project/table/route/adapter composition must be fixed before claimant row/token material enters; direct caller-created `ProviderEvidenceEnvelope` or caller-selected adapter/verifier cannot establish current provider provenance.

Semantic review:
- PR #102's mapper-vs-restore exception split is sound by static inspection. It starts restore-domain testing from a valid mapped row, then forges/re-digests the durable row independently, and requires provider-facing `PersistenceRecordError` with lower `ContractError` preserved as `__cause__`. Because its branch is stale/non-mergeable against current PR #64, use it as specification evidence until rebound; do not integrate blindly.
- PR #98 has a representation dependency to correct before source closure: its forced semantic fixture still emits string `trigger_provenance="FORCED_QUALIFICATION_ROUTE"`, while blocker #4's corrected authority design requires verified evidence provenance from a prebound authorization boundary. Shared receipt validation should enforce trigger/provenance semantics without freezing the legacy string representation as the only valid forced provenance shape. Do not weaken provenance to accept arbitrary mapping/string; bind the semantic validator to the eventual verified provenance schema.

PR #104 remains static-coherent / verification-open and queued behind affective closure. Blockers #2 and #6 remain source-integrated / execution-verification-open. No main merge, provider mutation/migration, fresh qualification/event, paid CI/spend, install/cutover, authority/memory promotion, or phenomenology promotion performed.