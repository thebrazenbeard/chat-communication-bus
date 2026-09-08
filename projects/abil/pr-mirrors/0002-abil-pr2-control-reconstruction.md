# ABIL PR Mirror — #2 Define ABIL control-reconstruction successor architecture

Source repository: `thebrazenbeard/abil`
Source PR: `https://github.com/thebrazenbeard/abil/pull/2`
State at mirror time: `OPEN / DRAFT / MERGEABLE / UNMERGED`
Base: `main@0812d9780ce1648820269fa142a43e17030ef793`
Head: `work/abil-control-reconstruction-architecture-20260908@c61405b395808a5bab5944d6324d1a638f09fbb1`
Observed at: `2026-09-08T07:17-04:00`
Changed files: 7
Commits: 11
Additions/deletions: `+1243 / -222`

## Purpose

Define the successor product architecture for ABIL as **replacement-capable, coexistence-first** brownfield control reconstruction while preserving the frozen 2026-09-06 F0/R1 source and FAIL result as historical evidence rather than rewriting it.

## Core product decision

ABIL should:

- work with surviving PLC logic by default;
- optionally use an existing PLC as deterministic execution proxy/permanent execution target;
- replace ordinary PLC control logic with a separately engineered ABIL deterministic control runtime when coexistence is impossible, undesirable, unsupported, locked, unreliable, failed, or uneconomic;
- keep intelligence/commissioning separate from deterministic execution;
- preserve independent safety authority by default.

## Changed living documentation

- `README.md`
- `docs/ARCHITECTURE_BOUNDARIES.md`
- `docs/COMPETITIVE_REALITY_CHECK.md`
- `docs/FIELD_VALIDATION_ROADMAP.md`
- `docs/PRODUCT_THESIS.md`
- `docs/superpowers/plans/2026-09-08-abil-control-reconstruction-product-architecture.md`
- `docs/superpowers/specs/2026-09-08-abil-control-reconstruction-product-architecture.md`

## Immediate review boundary

The PR explicitly does **not** make the next R2 subject a write-capable controller build. Immediate R2 remains a corrected early learning/telemetry substrate contract preserving the frozen R1 requirements. Write-capable commissioning, PLC proxy execution, direct remote-I/O control, deterministic runtime implementation, machine deployment, and cutover remain later separately qualified capabilities.

## Effect ceiling

No production control code, machine connection, deployment, credential/provider mutation, merge, or other protected effect is introduced by this PR at the mirrored head.

This mirror records source PR identity/current head for the singular Bus communication hub. Source PR lifecycle and merge authority remain in `thebrazenbeard/abil`.
