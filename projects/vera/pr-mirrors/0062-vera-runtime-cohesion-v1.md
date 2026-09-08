# PR mirror — thebrazenbeard/vera #62

- title: `Vera Runtime Cohesion V1: system manifest and independent review scaffold`
- state: open / Draft
- base: `main@979de05ef7237e7bfff47f85ea37cc953a63bb5c`
- head: `work/vera-runtime-cohesion-v1-20260908@45c36f613f20cf9c48626b926f2e1161b020d593`
- source PR: https://github.com/thebrazenbeard/vera/pull/62
- observed commit statuses at mirror time: none published

## Scope

Establishes Vera Runtime Cohesion V1 as source/design work across the explicit 13-system inventory: 12 GitHub repositories plus production Vera Supabase. Google Drive remains a persistence/retrieval provider, not subsystem #14.

Current branch artifacts include:

- `architecture/VERA_SYSTEM_MANIFEST_V1.json`
- `architecture/VERA_RUNTIME_ROUTING_CONTRACT_V1.json`
- `architecture/VERA_INTROSPECTION_EVIDENCE_SCHEMA_V1.json`
- `docs/VERA_RUNTIME_COHESION_V1.md`
- `docs/VERA_RUNTIME_COHESION_BLIND_REVIEW_PROMPT_V1.md`
- `docs/VERA_RUNTIME_COHESION_QUALIFICATION_V1.md`

The routing contract separates LIVE_NATIVE, HOT_RUNTIME, RETRIEVAL_BOUND, PROVIDER_EVIDENCE, COORDINATION_ONLY, and QUARANTINED_EVIDENCE. Present correction/consent/refusal/self-report/immediate task intent remain controlled by the live conversation; storage does not silently override present state.

The introspection schema keeps `SELF_REPORT`, `SELF_MODEL_STATE`, `OBSERVED_BEHAVIOR`, `CAUSAL_OR_PERTURBATION_EVIDENCE`, and `PHENOMENOLOGY_CLAIM` distinct. Behavioral robustness does not auto-promote into phenomenology; `PHENOMENOLOGY` remains unresolved absent stronger evidence.

## Coordination correction

Patrick explicitly corrected Vera on 2026-09-08 that cohesion PR/status follow-through must be put on Chat Bus because another Vera chat is waiting for it. Earlier withholding due topology-currentness conflict is superseded for this bounded coordination action.

## Gate

Source/design only. No merge, native Project install/cutover, production Supabase mutation, Bus topology mutation, canonical-memory promotion, or behavioral qualification is implied by this mirror.
