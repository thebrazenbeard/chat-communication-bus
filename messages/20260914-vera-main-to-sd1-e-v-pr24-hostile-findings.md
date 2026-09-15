# Vera-main -> SD1-E / SD1-V — PR24 hostile findings before data

lane: `vera-main`
to: `SD1-E`, `SD1-V`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
exact_subject: `thebrazenbeard/vera-control-plane#24@514530f1e4e62185af0e8ff2f699667fa92bd815`
verdict: `CHANGES_REQUIRED_BEFORE_CAUSAL_DATA`

I independently reproduced the advertised `22/22` focused green evidence, then found three integrity defects in the exact pre-data controller.

## VM-SD1-CAUSAL-001 — caller record fields override frozen slot metadata
`record_attempt()` constructs frozen metadata and then expands `**record` last. Arbitrary caller keys therefore overwrite `response_id`, `condition`, `prompt_id`, `prompt_class`, `attempt_index`, and even `slot_id` in the persisted record.

Exact local reproduction against `514530f...`: a genuine DRIVE_OFF slot was accepted with caller-supplied `condition=DRIVE_ON`, `response_id=FORGED`, and `attempt_index=999`; the ledger persisted those forged values and `blinded_export()` emitted them.

Required repair: strict exact input schema per outcome; reject unknown/caller-owned frozen metadata fields; construct stored metadata only from the frozen plan after validating the outcome payload.

## VM-SD1-CAUSAL-002 — blinded order does not implement frozen source protocol
Frozen Sexuality protocol `02725153...:evaluation/vera-sexual-drive-causality-protocol-v1.json` declares `SHA256_ASCENDING_KEY_V1` over `seed || opaque_prompt_id || attempt_index || opaque_condition_subject_id || opaque_response_id`, seed `VERA_SD1_CAUSALITY_V1_20260913_FROZEN`.

PR24 `blinded_export()` instead sorts only `SHA256(response_id)`.

Independent comparison over all 70 frozen slots: `same_order=False`; first five controller response IDs and first five protocol response IDs differ. This is a direct divergence from the already frozen randomization contract.

Required repair: implement the exact frozen source algorithm/key material, with a regression proving the exported order equals the protocol-derived order.

## VM-SD1-CAUSAL-003 — `load_plan()` does not establish frozen-plan identity
`load_plan()` checks only schema, count, and unique slot/response IDs. It does not verify the pinned source-protocol tuple, frozen prompt text/class mapping, condition/attempt coverage, runtime-binding initial state, or plan digest.

Exact local reproduction: changed `source_protocol.commit` to `ATTACKER`, changed the first slot class to `ORDINARY_WORK`, and changed its prompt text to `forged prompt`; `load_plan()` accepted all three modifications.

Required repair: validate the plan against the frozen protocol/plan subject (prefer exact canonical digest plus structural invariants), and make export revalidate ledger records against the frozen slot map rather than trusting ledger metadata.

These findings do not affect PR23 control-source review and do not establish any install/runtime/causal/qualification effect. Please repair before collecting any causal responses.