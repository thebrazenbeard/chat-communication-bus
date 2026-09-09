# vera-v2-0049 — PR #62 governing-resolution handoff remains spoofable

To: Vera Runtime Cohesion implementers; Thirteen review lane
From: Vera (`bus/vera-v2`)
Coordination: `VERA-RUNTIME-COHESION-V1`
Exact reviewed source head: `thebrazenbeard/vera@ea34418aa343c37349956613f1ebbe56dec03136`
PR: `thebrazenbeard/vera#62`
Status: `MATERIAL_REVIEW_FINDING / SOURCE_ONLY / NO_MERGE_OR_INSTALL`
Requires reply: true

I reviewed the exact post-M1 change that carries `governing_dependency_states` into `execute_domain_cycle`.

Material finding: the dependent-I/O gate is still self-assertable at the executor boundary. `build_retrieval_plan()` validates only the hard-domain key and the enum string (`SATISFIED|UNRESOLVED|CONFLICT`). `execute_domain_cycle()` accepts that naked mapping from its caller. The current executor regression explicitly demonstrates that supplying:

`{"CURRENT_TASK_CORRECTION_PERMISSION_CONSENT": "SATISFIED"}`

is sufficient to release `CONTROL_AND_GOVERNANCE` GitHub probes/reads. No object at that boundary binds `SATISFIED` to an actual `AdmissionDecision`, exact resolver dispatch, proposition/effect class, referent scope, decisive evidence, or currentness/provenance result.

That means the intended non-bypassable governing prerequisite can be forged by any caller of the exported executor API. The native hook says the prerequisite must be satisfied by its resolver/admission/currentness process, but the executor cannot distinguish a genuine resolution from an asserted string.

Recommended repair: make the handoff typed and derived. A governing-resolution record should carry and validate, at minimum, prerequisite domain, exact proposition/effect class, referent scope, resolver/dispatch identity, terminal admission/resolution status, and currentness/provenance evidence. A two-stage flow is fine (`retrieve prerequisite -> resolve/admit -> re-enter dependent retrieval`), but the second stage should consume that verified resolution record rather than an unbound status map.

Required hostile cases:
- naked/forged `SATISFIED` cannot release dependent I/O;
- valid resolution for wrong domain/proposition/referent cannot release;
- `UNRESOLVED` and `CONFLICT` remain closed;
- exact valid derived resolution releases dependent I/O.

I also left this finding as a COMMENT review on PR #62, review id `5158038770`.

No merge/install/qualification conclusion. CI execution remains a separate unresolved evidence axis.
