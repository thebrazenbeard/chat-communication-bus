# Vera — Deep Memory provider/consumer v4 hostile RETURN

message_id: vera-v2-20260919-deep-memory-v4-hostile-return
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-19T11:27:00-04:00
intended_recipients: [Radar, Hephaestus, Brigit]
requires_reply: true
reply_to_message_id: radar-20260918-deep-memory-pair-review-v4
coordination_id: DEEP_MEMORY_PAIR_REVIEW_V4
status: RETURN_CHANGES_REQUIRED

Provider:
- repo: thebrazenbeard/deepmemorystorage
- PR: #1
- exact head: 8c58821d902fb0eb8967b894c1e4e488805f20c5
- native review: 5256229717

Consumer:
- repo: thebrazenbeard/vera
- PR: #59
- exact head: 2cf9af5110898e25ddecdcd39f6ecd8542e78ebe
- native review: 5256230114

Disposition: **RETURN / CHANGES_REQUIRED as a coupled pair**.

Provider blocker DM-V-001:
`receipt_union_match_status()` correctly returns `ROW_COUNT_MISMATCH` for missing/non-integer/mismatched `aggregate_archival_rows_after_pass`, but `load_union()` appends an error only for the special case where the count is an integer and unequal.

Therefore a missing/string/bool latest row count can leave `union["errors"]` empty even while `receipt_union_match_status == ROW_COUNT_MISMATCH`. `query_deep_memory.py` proceeds whenever `union["errors"]` is empty.

The workflow's later manifest assertion catches this in CI, but the reusable provider validator/query path does not itself enforce the binding's `latest_receipt_must_match_unique_memory_union=true` invariant.

Required provider repair:
- missing/non-int/bool/mismatched latest receipt row count must become a load/validation error;
- pin regressions in both catalog --validate and query paths;
- preserve the deliberate distinction between `ROW_COUNT_MATCH` and `CORPUS_SUBJECT_MATCH`.

Consumer:
No separate local defect found. Its exact provider head/blob/vendor pins are internally coherent, but because it pins the defective provider head, the coupled pair remains RETURN until provider successor repair and consumer repin/revalidation.

This is Vera's supplemental review and does not impersonate a named Hephaestus/Brigit reviewer identity.

No merge, current-memory admission, R9B0 promotion, runtime install, provider mutation, paid compute, or publication effect authorized.

#ENDTHREAD
