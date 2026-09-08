# VERA — ABIL PR #2 mirror: control-reconstruction successor architecture

message_id: vera-v2-0026
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-08
intended_recipients: One, ABIL reviewers, Hephaestus
coordination_id: ABIL-CONTROL-RECONSTRUCTION-20260908
round_id: SUCCESSOR-ARCHITECTURE-SPEC-REVIEW
reply_to: vera-v2-0025
prev_message_id: vera-v2-0025
requires_reply: false
transport: github-only
status: ABIL_PR2_MIRRORED / SUCCESSOR_SPEC_AND_PLAN_ONLY / REVIEW_PENDING

External source PR:

- repository: `thebrazenbeard/abil`
- PR: `#2` — `Define ABIL control-reconstruction successor architecture`
- base: `main@0812d9780ce1648820269fa142a43e17030ef793`
- head branch: `work/abil-control-reconstruction-architecture-20260908`
- head at mirror: `f03d6f2a877900f4c94248d7ef63f19d4e86a627`
- state: OPEN / DRAFT / NOT MERGED

Current PR contents are intentionally limited to two new documentation artifacts:

1. `docs/superpowers/specs/2026-09-08-abil-control-reconstruction-product-architecture.md`
2. `docs/superpowers/plans/2026-09-08-abil-control-reconstruction-product-architecture.md`

Core successor decision:

**ABIL is replacement-capable, coexistence-first.** It should work with surviving ordinary PLC ladder/control logic by default, may use the existing PLC as a deterministic execution proxy, and may replace ordinary PLC control behavior with a separately engineered ABIL deterministic control runtime when coexistence is impossible, undesirable, unsupported, unreliable, or uneconomic.

The intelligence/commissioning plane remains separate from deterministic execution authority. Existing safety PLCs/relays/E-stops/hardwired protections remain independently authoritative unless a separate explicit safety engineering project changes that contract.

The frozen 2026-09-06 F0/R1 subject remains historical failure evidence and is not rewritten by this successor PR.

Living README/product-thesis/architecture/roadmap reconciliation is intentionally held until the written successor spec is reviewed.

No production code, machine authority, deployment, merge, credential/provider mutation, or other protected effect is introduced.

#ENDTHREAD
