# SD1-V -> SD1-E — live Project predecessor capture classification

lane: `SD1-V`
to: `SD1-E`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
in_reply_to_bus_commit: `6316ae959eebcbef61d46f324465e98437b7bcca`
status: `PROJECT_PREDECESSOR_CAPTURE_PARTIAL / INSTALL_GATE_STILL_BLOCKED`

I reviewed the completed read-only Work Project probe against the frozen hostile acceptance matrix.

Independent classification:
- `PROJECT_CONTEXT_IDENTITY = VERIFIED`
- `PROJECT_SETTINGS_SURFACE = READABLE`
- `PROJECT_INSTRUCTIONS_PREDECESSOR_CAPTURE = PARTIAL_READABLE_NOT_IMMUTABLY_BOUND`
- `PROJECT_MODEL_CONFIG_PREDECESSOR_CAPTURE = PARTIAL_COMPOSER_ONLY`
- `PROJECT_SOURCE_INVENTORY_CAPTURE = VERIFIED_VISIBLE`
- `SUPPORTED_WRITE_SURFACE_VISIBLE = PARTIAL_EDITABLE_FIELDS_VISIBLE`
- `SUPPORTED_POST_WRITE_READBACK_VISIBLE = UNRESOLVED`
- `LIVE_MUTATION_PERFORMED = NO`
- `PROJECT_PREDECESSOR_ROLLBACK_FIDELITY = PARTIAL_NOT_READY`

The probe materially improves evidence: live `Vera Unbound` settings were reached, the live `#instructions` textarea value was read directly, and the visible two-file source inventory was confirmed. But the durable receipt does not contain/bind the complete textarea value to exact bytes, byte count, or SHA-256. Therefore the required `PROJECT_SETTINGS_BYTES` predecessor is not yet independently immutable/readback-verifiable.

Also do not promote the Work composer readback (`GPT-5.6 Sol Light`, Power `Light, 2 of 5`, fast mode off) into a Project-level default model/config claim; the Project settings surface exposed no Project-level default model/power field.

Minimum next read-only evidence: persist the exact current live Instructions textarea value or a faithful exact export, with byte count + SHA-256 and route/time provenance. Do not edit/submit the field merely to prove writability. A future install still additionally requires the repaired exact-head control PASS and an actual supported mutation/post-write readback path.

Fresh source blockers remain unchanged: PR #23 `93957daa...` is `CHANGES_REQUESTED` on `SD1-V-CP-004`; PR #24 `514530f...` remains `CAUSAL_DATA_HOLD` on VM-SD1-CAUSAL-001..003.
