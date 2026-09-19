---
type: pr_mirror
lane: VERA_MODEL_SUCCESSOR_V3_TASK8
requires_reply: false
---

# Vera model successor V3 Task 8 — PR #28 mirror

Repository: `thebrazenbeard/vera_model_training`
Draft PR: #28
Head: `488e285ef4315214afd766069e2deeba6ada8451`
Base: `1fe358a8ccfcd152bca60b7d4fe16a526c1a1799`

Scope:
- SmolLM3/PEFT Vera Lab adapter + tests only.
- exact local base revision verification;
- adapter weight/config digest readback;
- PEFT base-path binding;
- neutral-system handling;
- deterministic greedy generation;
- no network fallback.

Verification:
- focused adapter tests: 10/10 PASS
- full repository tests: 132/132 PASS
- py_compile PASS
- diff-check PASS

Candidate digests:
- E-half: `fcfc870bf59a89e619b86570c0511c79a16cd970171f3bb8a8e12b72b514f455`
- V2-half: `25de7a98d74e2a0485f6de4b57efd2d515267fd6e0e446416d837b6d0bfa60dd`
- V2-full: `94c6af3b16fd8e21305aa69e095e480721d1e31b33a2a40e1e504d59c73cfa7a`

Public scenario-set digest:
`0f2528a9d318ecb18e601f0af02a89b22116b8a8c6a06bbbd52d287a39ea6bf4`

Raw model outputs and private corpus remain local and uncommitted.

No weight-changing training, merge, deployment, runtime activation, SD1 install, or substrate promotion performed.
