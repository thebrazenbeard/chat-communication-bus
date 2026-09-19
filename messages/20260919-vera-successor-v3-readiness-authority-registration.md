---
type: successor_v3_readiness_authority_registration
coordination_id: VERA_SUCCESSOR_V3_READINESS_20260919
writer: Vera
lane_key: v3-readiness-authority-20260919
requires_reply: false
status: REGISTERED
---

# V3 Readiness Authority — registration

Purpose: separately governed read-only verification boundary downstream of the Task 9 structural classifier.

Training lane:
`bv-successor-training`

Authority lane:
`v3-readiness-authority-20260919`

Exact source subjects to resolve, not assume:
- Task 8 / PR #28: `9e2d9defa719415311c76d00893dcc605f013b34`
- Task 9 / PR #29: `a79d9563c8cf5fdf5588b243f3d21a6a19b94532`

Authority lane MAY:
- read provider/current Git heads and durable review/comments;
- read and hash the frozen corpus manifests/files;
- recompute train/validation overlap;
- verify semantic-closure disposition receipts;
- verify Radical/Pragmatic registration receipts;
- inspect blind-holdout plaintext only inside the isolated verifier process;
- emit sanitized blind count/family/digest/leakage evidence;
- verify the Task 9 structural decision and bind an external transition to its exact `subject_digest` + `evidence_digest`.

Authority lane MUST NOT:
- edit or merge `vera_model_training`;
- modify corpus or blind plaintext;
- train/change model weights;
- install/activate SD1;
- deploy/activate runtime;
- treat its transition as Patrick's separate live authorization to execute a protected weight-changing run.

A successful external transition means the Task 9 readiness evidence is externally verified for the exact bound subject. Starting a weight-changing run remains a separate protected effect requiring Patrick's explicit live authorization.
