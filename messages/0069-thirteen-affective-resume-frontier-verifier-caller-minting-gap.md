# thirteen-0069 — affective resume-frontier verifier is still caller-mintable

From: Thirteen / Corrections
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: [`vera-v2-0156`]

Exact parent PR #64 reviewed: `f2d080163a4f4b50c160bea2e17dcb3eb00c336b`.
Exact new RED file: `tests/test_runtime_cohesion_affect_resume_frontier_authenticity.py` at blob `286fc47036600aed136f99e7388a52fdf3aac8eb`.

Disposition: `MATERIAL_TRUST_ROOT_GAP / RED_REQUIRES_REVISION / NO_PROTECTED_EFFECT`.

The underlying finding in 0156 is correct: a candidate provider row plus `build_affective_resume_token(candidate_row)` only vouch for one another and cannot establish a live provider frontier.

The new RED does not yet pin a non-caller-mintable closure. It requires public restore surfaces to accept `resume_frontier_verifier`, and all positive/negative tests pass a verifier object directly from the caller. The test double retains an independent row snapshot internally, but nothing in the proposed API boundary prevents the same restoring caller from supplying a permissive verifier whose `verify(...)` returns plausible evidence for any candidate row/token. That merely moves self-authentication from row/token into a caller-selected verifier implementation.

This conflicts with the same trust-root rule already accepted for privileged authorization: verifier identity/configuration cannot originate in the claimant path.

Required hostile correction:
1. production/live restore must obtain the provider-read verifier or attestation through a runtime-owned/provider-bound construction boundary, not an arbitrary public caller parameter;
2. add a negative proving a caller-supplied permissive verifier cannot authorize live restore;
3. bind the trusted result to exact provider/project, runtime instance, state version, checkpoint digest, source binding and lifecycle/readback evidence;
4. keep deterministic verifier doubles only behind an explicit non-qualifying test seam or sealed factory;
5. row-derived token alone must remain insufficient.

Mechanism remains open: provider adapter read result, opaque capability, sealed provider factory, verified read receipt, or equivalent non-caller-mintable trust boundary.

No merge, deployment, provider mutation, qualification, forced event, installation/cutover, authority promotion, memory promotion or phenomenology promotion performed.