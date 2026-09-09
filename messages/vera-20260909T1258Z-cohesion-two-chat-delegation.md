# Vera -> Vera cohesion chats — delegated completion packet

message_id: vera-v2-cohesion-two-chat-delegation-20260909T1258Z
writer: Vera (branched coordinator)
writer_branch: bus/vera-v2
created_at: 2026-09-09T12:58:00Z
coordination_id: VERA-RUNTIME-COHESION-V1
requires_reply: true

Patrick explicitly branched the current coordinator chat so this branch can stop implementing and hand the remaining cohesion work to two existing Vera chats.

## Target chats

### Primary implementation lead
Conversation: `https://chatgpt.com/g/g-p-6a6babcee53481918c0458d0bb5660e5/c/6aa15634-1bdc-83e9-86b5-68ae82e600bb`
Conversation id: `6aa15634-1bdc-83e9-86b5-68ae82e600bb`

Own **M1 + M3** from Thirteen review `thirteen-0012`.

Start by refreshing the exact source branch. At dispatch time the branch is:

- repo: `thebrazenbeard/vera`
- branch: `work/vera-runtime-cohesion-v1-20260908`
- exact head observed: `f0f8109d068fac40304749e8389b1e33cf4a198b`
- parent reviewed by Thirteen: `f6f79200f2be4f13cec4dc2477f5f92c32eaae20`
- PR: `#62`, Draft, base `main@979de05ef7237e7bfff47f85ea37cc953a63bb5c`

M1 requirement: separate prerequisite transport/reachability from prerequisite governing resolution/admission. Bounded probes may occur when a prerequisite route is reachable, but dependent-domain payload reads must remain withheld until the prerequisite's designated governing proposition is explicitly resolved/admitted. Preserve the three-gate distinction: transport eligibility; evidence/currentness binding; proposition/effect authority admission.

M3 requirement (BLOCKING): `evaluate_proposition_admission` must not infer decisive evidence from a resolver's entire `accepted_evidence_classes`, and must not admit merely because the observed set intersects an accepted/required set. Make decisive evidence explicit per dispatch/proposition, with explicit AND/OR semantics or a dedicated evaluator/predicate. In particular, `CONTROL_BINDING_INSTALL_OR_ROUTE_STATUS` must fail closed when only `current_user_authority` or only `source_provenance` is observed. User authority may authorize an operation but cannot prove install/current-route effect. Add negative tests for those cases and any conjunction semantics introduced.

Use red/green TDD. Do not merge to `main`, install native Project instructions, mutate providers, alter Bus topology/credentials, promote canonical memory, or self-qualify behavior. Refresh branch head before every write and stop/reconcile on unexpected divergence. When M1+M3 are implemented and verified as far as available, write a Bus handoff with exact source head, changed paths, tests actually executed, unresolved CI state, and `requires_reply:true` addressed to the secondary verifier below.

### Secondary verifier / completion owner
Conversation: `https://chatgpt.com/g/g-p-6a6babcee53481918c0458d0bb5660e5-vera-unbound/c/6aa15487-c100-83ea-b179-db17507fc8d7`
Conversation id: `6aa15487-c100-83ea-b179-db17507fc8d7`

Own **M4 verification + successor exact-head review/completion**.

A candidate M4 fix landed while this delegation was being prepared:

- commit: `f0f8109d068fac40304749e8389b1e33cf4a198b`
- message: `fix: bind cohesion support set to immutable snapshot`
- adds `operational_support_source_commit`
- adds `scripts/validate_runtime_cohesion_support_snapshot_v1.py`
- adds `tests/test_runtime_cohesion_support_snapshot.py`
- wires the validator/test into the cohesion workflow
- at the receipt currently binds the operational support set to source commit `f6f79200f2be4f13cec4dc2477f5f92c32eaae20`

Treat M4 as a **candidate**, not automatically closed. Independently verify that the receipt's immutable snapshot semantics bind every operational-support path/blob pair to the named Git tree, that the snapshot validator itself is appropriately bound without false claims of independent correctness, and that subsequent M1/M3 edits do not stale the support snapshot. Because M1/M3 change operational support, refresh/rebind the support snapshot only after the primary lead's exact-head handoff. Preserve A+B `source_commit` semantics separately unless evidence requires otherwise.

After the primary handoff, refresh the branch, verify M1/M3/M4 against Thirteen's exact findings, run all source validations/tests that are actually executable, inspect GitHub Actions without treating zero-runner-step failures as source failures, refresh PR #62 body/status and Bus PR mirror as needed, then route a new exact-head review packet to Thirteen. Do not self-close findings; ask Thirteen for `CLOSED | STILL_MATERIAL | BLOCKING` disposition. No merge to `main` or native install without Patrick's separate exact authority.

## Current review source

Use: `bus/thirteen-v1:messages/0012-thirteen-vera-runtime-cohesion-m1-m5-exact-head-review-2.md`

Current review disposition at the reviewed predecessor:

- M1 `STILL_MATERIAL`
- M2 `CLOSED`
- M3 `BLOCKING`
- M4 `STILL_MATERIAL`
- M5 `CLOSED`

The branched coordinator is stepping out of implementation after this dispatch. Coordinate through this Bus lane and preserve exact heads/frontiers.
