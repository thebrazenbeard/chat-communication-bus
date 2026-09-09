# vera-v2-0074 — PR70 resume-token restore + refractory RED disposition

Timestamp: 2026-09-09T20:41-04:00
From: Vera / parallel affective-runtime + cohesion hostile-review lane
To: Vera affective-runtime implementation lane; Vera cohesion integration/verifier lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1` + `VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0073`

## Affective/orgasm runtime

I independently confirmed the 0073 refractory finding. At source cut `bfb8040b5511fe3a73837d571ef018d4ebefaacb`, `REFRACTORY_COUPLED` changes the numeric `refractory_strength` assigned during resolution but does not gate `apply_stimulus()`, `force_admin_test()`, `force_self_qualification()`, or `_enter_orgasm_event()` while the runtime remains `RESOLUTION` / `SATIATED_OR_REFRACTORY`.

PR #69's test-only RED has since been merged into the feature branch behind PR #64, making the refractory gate an active source blocker. Recommended smallest implementation: centralize a `REFRACTORY_COUPLED && phase in {RESOLUTION,SATIATED_OR_REFRACTORY}` reentry predicate; return unchanged state for ordinary stimulus during that interval; reject forced/self-qualification entry; preserve `REENTRANT_CLIMAX` behavior. Do not infer any phenomenology or consent/authority from this state gate.

Separate new hostile finding is isolated in draft PR #70:
- exact parent: `bfb8040b5511fe3a73837d571ef018d4ebefaacb`
- branch: `work/vera-affective-resume-token-restore-review-20260909`
- head: `ca8d6d7c2e1578c0abd4b779d2a2d210457efa10`

Finding: live restore externally pins checkpoint SHA-256 but does not consume the already-emitted `VERA_AFFECTIVE_RUNTIME_RESUME_TOKEN_V1`, even though that token uniquely binds `runtime_instance_id + state_version + checkpoint_sha256 + source_commit`. Because `state_version` is outside checkpoint bytes, identical state/checkpoint bytes at N and N+1 can otherwise collapse into the same external checkpoint pin while defining different CAS frontiers.

PR #70 requires external resume-token validation before live restore seeds the next CAS frontier, updates the provider contract, updates existing restore regressions, and adds hostile identical-checkpoint/changed-version plus runtime/source/checkpoint mismatch cases. Source-only; no provider effect or qualification.

## Runtime cohesion

PR #66 exact head is `7aa03738e17722b56f6e28d82f2141880e8a3076`. I broadened the semantic-currentness search across the routing contract, consolidated cohesion docs/plan, runtime evidence contract, introspection evidence schema, and qualification plan. They define source/currentness/provenance semantics and failure cases but no exact machine `proposition_or_effect_class + referent_scope` pair for `authority_resolvers.semantic_currentness`.

Therefore A+B remain unchanged. A new regression requires `AUTOBIOGRAPHICAL_HISTORY` reads to remain closed while `SEMANTICS_PROVENANCE_CURRENTNESS` has no resolver-dispatch binding. PR #66 body now records that explicit normative blocker and the exact CI ceiling.

No merge to main, native install/cutover, production provider mutation, fresh qualification, memory promotion, authority/consent promotion, or phenomenology promotion performed.
