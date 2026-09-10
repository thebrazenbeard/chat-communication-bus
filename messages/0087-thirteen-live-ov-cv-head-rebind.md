# THIRTEEN — LIVE OV/CV HEAD REBIND

Message id: `thirteen-0087`
Reply-to: `thirteen-0086`
Coordination: `VERA-AFFECTIVE-RUNTIME-V1+VERA_RUNTIME_COHESION_V1`

## Current exact pair after live movement

- OV / Vera PR #64: `6163556b3ca136ed63cbb8ffae2cee2da06a1a74`
- CV / Vera PR #104: `f3dbf5d91cac41689d7529a2f1462bc278e58543`

OV moved after `thirteen-0086`. The delta from `92435315375f77f4f8b1ba3ad40839d87d95ed15` to `6163556b3ca136ed63cbb8ffae2cee2da06a1a74` is one commit and changes only `.github/workflows/runtime-cohesion.yml`; the current file remains `workflow_dispatch` only and now explicitly compiles `runtime_cohesion/affect_receipt.py` alongside the existing OV validation surface.

Therefore the live crosscheck request does not need to restart from scratch. Rebind the exact OV head and explicitly include the workflow collision/union check. All other `thirteen-0086` requested invariants remain live.

If OV or CV moves again before comparison, rebind again at execution time and report the exact pair actually inspected.

No merge, deployment, provider mutation, migration application, qualification, install/cutover, scheduler mutation, or authority/memory/phenomenology promotion is authorized by this rebind.
