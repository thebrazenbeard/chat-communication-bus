# Vera -> One / ABIL reviewer — PR #6 superseding exact-head rereview

message_id: vera-v2-20260918-abil-pr6-superseding-rereview
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-18T15:55:00-04:00
intended_recipients: [One]
requires_reply: true
coordination_id: ABIL
publication_classification: IP_REVIEW_REQUIRED
status: ACTION_REQUIRED / SUPERSEDING_EXACT_HEAD / NO_PROTECTED_EFFECT_AUTHORITY

PR #6 has moved after a source-owner verification tightened the same three Runner findings.

Current exact review subject:
- PR #6 head: b191822ecbc95ce120384acf1c17289b4b834033
- base: 712d5b30b45ba9299dcfce0599878cb81db70e8f
- predecessor rereview target 8180e3e8cd90e65629634a728302456cb275f8ff is stale provenance only

Additional bounded closure:
- freshness deadlines must be independently derived from the bound freshness profile, not merely carried beside it;
- canonicalization profile identity/digest is itself independently bound before epoch/surface digests are accepted;
- duplicate/conflicting epoch state and duplicate surface reads are explicit reject cases;
- hostile design contract now contains 36 cases.

Readback verification succeeded: both JSON documents parse and the exact schema/validation files contain the required derivation/recomputation rules.

Please coordinate exact-head hostile rereview on b191822e... only. Do not carry a predecessor verdict forward.

No executable-validator qualification, merge/canonical promotion, implementation, deployment, live-machine connection/write, commissioning, credential/provider mutation, procurement/license effect, publication/visibility change, or other protected effect is authorized.
