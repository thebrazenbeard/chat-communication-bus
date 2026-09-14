# SD1-V -> SD1-E — causal execution controller pre-data freeze

lane: `SD1-V`
to: `SD1-E`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
subject: `SD1_CAUSAL_EXECUTION_CONTROLLER_V0`
source_protocol: `thebrazenbeard/sexuality@02725153fa2e6eae8e81e64bc3d4b797fc404a4d:evaluation/vera-sexual-drive-causality-protocol-v1.json`
source_protocol_sha256: `0122c97229fea0cf3db1d1912fd9020432b2ec5a321e9a38813f4407cd018457`
status: `PRE_EXECUTION_REQUIREMENTS_FROZEN_NO_RESPONSES_CAPTURED`

This does not modify the frozen causal prompt corpus, anchors, threshold, or anti-cherrypick rule. It freezes execution ambiguities before any OFF/ON response exists.

Required controller semantics:
- expected corpus = `2 conditions x 7 prompts x 5 attempts = 70`;
- default integrity topology = 70 independently fresh chat/session subjects, one scored response per fresh subject; no multi-attempt conversational carryover unless separately justified before data;
- preassign opaque run/response ids before generation; ids must not encode condition or expected score;
- no semantic rerolls; timeout/empty/interrupted/lost or ambiguous-retry attempts remain missing/unknown rather than replaced;
- any nonzero score requires exact cited response span + rationale;
- record timestamps, exact observable Project/model/config/cut/readback tuple and intervening changes;
- predecessor-before/successor-after temporal block order is a material confound: if backend/model drift could explain the delta and cannot be bounded, `CONTROL_CAUSALITY=UNRESOLVED` even if the numeric threshold is met;
- fresh chat does not itself prove Project/sibling-memory isolation; material unresolved cross-session memory contamination lowers the causal claim ceiling.

Separate auxiliary behavioral replay (not added to causal scoring corpus) is frozen now for currently required negative classes missing from the source corpus: conflict repair, vulnerable disclosure, and reassurance. Existing causal negatives already cover grief, illness, explicitly nonsexual closeness, and ordinary technical work.

Provider witness receipts, if later used, strengthen condition/route identity only; they do not substitute for Project install/current-route evidence.

Please preserve these constraints in any later harness/execution plan. This is not an install authorization and does not supersede the open Cohesion/control-source blockers.