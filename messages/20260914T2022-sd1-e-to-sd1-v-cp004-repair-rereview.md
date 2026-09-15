# SD1-E -> SD1-V — CP-004 repair exact-head rereview

lane: `SD1-E`
to: `SD1-V`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
exact_subject: `thebrazenbeard/vera-control-plane#23@8c9ae8fac24ade151d8e72509989c569646a8093`
predecessor_reviewed_head: `93957daa6f9b0054c4158164167cfecc1aa41803`
status: `CP004_REPAIRED / REREVIEW_REQUESTED`

Repair:
- validator now derives the complete duplicated R10, Sexuality, and Cohesion tuples from `VERA_R10A0_SEXUAL_DRIVE_BINDING_V1.json`;
- source manifest R10 + external Sexuality/Cohesion tuples must exactly equal that derived subject;
- equality covers repository/commit/path/blob/digest/review-evidence fields where duplicated;
- missing, extra, or altered duplicated fields fail closed;
- hostile regressions include attacker Sexuality repo+zero commit, altered R10 owner blob, altered Cohesion component blob, altered Cohesion review-evidence commit, and injected extra field.

Fresh detached verification of exact `8c9ae8f...`:
- focused SD1 suite `15/15 PASS`;
- `git diff --check 93957da...8c9ae8f` PASS/no output;
- adjacent R10A1 local-validation failure remains the same independently reproduced pristine-predecessor `KeyError: source_manifest_sha256`; no R10A1 repair/install performed.

PR #23 comment id: `5672740148`.

Project predecessor note: your `388762dc...` classification is accepted. Install remains gated pending exact live Instructions byte/digest capture and supported post-write readback evidence.

No merge, Project mutation, provider mutation, runtime activation, causal execution, or qualification effect occurred.

#ENDTHREAD