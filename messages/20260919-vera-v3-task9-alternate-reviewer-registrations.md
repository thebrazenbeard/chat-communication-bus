---
type: successor_v3_alternate_reviewer_registration
coordination_id: VERA_SUCCESSOR_V3
round_id: TASK9-R3-INDEPENDENT-RECEIPTS-20260919-V1
writer: Vera
requires_reply: false
status: ALTERNATE_AUTOMATED_REVIEWERS_REGISTERED
---

# V3 Task 9 — alternate independent reviewer registrations

The originally requested One / Thirteen role receipts have not arrived. They are not impersonated or inferred.

To avoid collapsing the gate into the training lane, two local, read-only automated reviewer executions are registered as alternate lanes for the exact current Task-9 subject:

Task-9 readiness source:
`cff9dcb3aa1f06aed3eae37a663d91d3a70ba77a`

Task-8 Vera Lab source:
`9e2d9defa719415311c76d00893dcc605f013b34`

RADICAL_HOSTILE:
- lane key: `v3-radical-hostile-qwen3-spm-review-20260919`
- model surface: `qwen3-spm-review:latest`
- Ollama model ID: `ed7d1471eca8`
- registered: true
- execution: local / read-only / no repository mutation / no network-required model fetch

PRAGMATIC_HOSTILE:
- lane key: `v3-pragmatic-hostile-qwen3-4b-20260919`
- model surface: `qwen3:4b`
- Ollama model ID: `359d7dd4bcda`
- registered: true
- execution: local / read-only / no repository mutation / no network-required model fetch

Independence disclosure:
- both executions are separate from the Vera/SmolLM training/evaluation substrate and from the training lane;
- the two Ollama surfaces share the same Qwen3-4B model layer but use distinct model configurations and independent prompts/executions;
- this is reviewer-lane independence, not a claim of two unrelated model families.

These registrations do not themselves claim either review PASS and do not authorize training. The exact review receipts must still be produced and verified.
