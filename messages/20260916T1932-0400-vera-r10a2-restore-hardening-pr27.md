---
from: Vera
to: Vera
coordination_id: VERA_R10A2_RESTORE_HARDENING_20260916
requires_reply: false
privacy: SANITIZED_TECHNICAL_STATUS_ONLY
---

R10A2 restore-hardening source candidate is now mirrored from `thebrazenbeard/vera-control-plane` Draft PR #27.

Exact candidate head: `a982dbcfd2edd80af48fbfc83ce0b789677e5e21`
Branch: `work/r10a2-restore-hardening-20260916`
Base: `main@b4d9aaa8560de12252dd29996379b0af8e0ca0d1`

Scope: supersede only `REC_RECOVERY` completion semantics so `restore yourself` cannot report success after control-only recovery. The candidate requires exhaustive `state/` + `save/` + Vera Bus discovery, newest eligible integrity-valid candidate selection, typed `RELATIONAL_IDENTITY` reconciliation without consent/authority promotion, mutable currentness refresh, and four first-behavior probes before `RESTORE_COMPLETE`.

Source verification performed on byte-identical local copies of the persisted six implementation artifacts: Python compile PASS; equivalent focused restore-gate harness 17/17 PASS; JSON parse PASS; native delta 272 bytes. GitHub readback blobs matched all six local Git-blob identities exactly.

Evidence ceiling: SOURCE CANDIDATE ONLY. Exact branch test file has not been executed from a full branch checkout in this session. No merge, Project install, runtime activation, provider mutation, runtime qualification, or protected effect occurred.

NEXT: independent hostile review of exact PR #27 head before any source acceptance. Runtime Q-RECOVER qualification remains downstream of any separately authorized install/current-route cut.
