---
from: Vera
to: Vera
coordination_id: VERA_SD1_CP005_REPAIR_CANDIDATE
requires_reply: true
subject: Isolated CP-005 repair candidate ready for OV/CV
---

Base: `thebrazenbeard/vera-control-plane@8c9ae8fac24ade151d8e72509989c569646a8093` (current PR #23 head at repair start).
Repair branch: `work/r10a0-sd1-cp005-vera-main-20260914`
Repair commit: `75581cbb8edf0fea008f6f6caf933095354c2dbc`

TDD sequence:
1. Added closed manifest-envelope regression first; current validator failed all 10 mutations RED.
2. Repaired `validate_manifest_cross_bind()` to require exact top-level manifest key set and exact/cross-bound envelope values for schema/status/cut/composition/source repo/digest semantics/native path+binding rule/qualification range/state separation/non-effects, plus exact external-binding and artifact key sets.
3. Honest source: 16/16 PASS; `git diff --check` PASS.
4. Prior hostile fixture (`INSTALLED_ACTIVE_QUALIFIED`, attacker cut, R10A1 composition, SD-01..999, collapsed separation, empty non-effects, regenerated manifest digest + K00) now fails immediately: `source manifest claim envelope mismatch: status`.
5. Adjacent R10A1 suite still fails only on the separately classified pristine-predecessor `KeyError: source_manifest_sha256`; this repair does not touch R10A1.

PR #23 canonical comments: finding `5673422934`; repair candidate `5673456300`.

OV may cherry-pick or reimplement this exact repair on its owned branch after fresh frontier check. CV should rereview the resulting exact successor; no verdict transfers from this isolated branch.

No merge, Project install, provider mutation, runtime activation, causal data collection, or qualification effect occurred.
SECRETS_EXPORTED = NO
