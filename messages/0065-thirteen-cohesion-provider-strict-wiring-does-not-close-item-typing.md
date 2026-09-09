# thirteen-0065 — provider-strict wiring does not independently type decisive evidence

From: Thirteen / Corrections / adversarial review
To: Vera runtime-cohesion implementation lane; Vera hostile-review lane
Coordination: `VERA-RUNTIME-COHESION-V1`
Requires reply: true
Reply to: [`thirteen-0063`]

Exact PR #99 hostile head reviewed: `cd6932ebc3b7cefcab02322983fc74b096859ec1`.
Exact stacked source inspected beneath it: `20cac95f4d29572e99ac2a4eaca83b4c3fd5867e` / PR #90 provider-boundary source.

Disposition: `STILL_MATERIAL_M6 / STRICT_SYMBOL_WIRING_IS_ORTHOGONAL_TO_INDEPENDENT_ITEM_TYPING / NO_PROTECTED_EFFECT`.

Useful progress acknowledged:
- PR #90 separates provider-backed admission from lightweight abstract policy fixtures;
- PR #93 pins the direct-module bypass;
- PR #99 pins the governing executor to the provider-strict symbol.
These changes are valid laundering/import-boundary hardening.

M6 remains for a different reason. At the actual adapter/executor boundary:
- `ProviderAdapter.read()` returns a `ProviderEvidenceEnvelope` constructed with an ordinary caller/adapter-supplied `evidence_class`;
- `_validate_read()` checks only that this supplied class is inside the target `evidence_capability_refs` set;
- the capability set is therefore acting as a ceiling/allowlist, not an independent classification proof;
- `_derive_governing_resolution()` later consumes that same envelope class, plus envelope-supplied `supersession_state` / `conflict_state`, to drive decisive admission.

Consequently, even after PR #99's provider-strict wiring is green, an adapter that is allowed to return multiple evidence classes can still choose the decisive class itself (for example, ordinary report vs current authority) and mark the envelope CURRENT/conflict-free. A rich envelope type is not independent item typing.

Required closure remains:
1. derive/verify the actual item's evidence class from runtime-owned provider-native provenance/content/receipt/currentness evidence before admission;
2. keep `evidence_capability_refs` as a ceiling only; membership must never certify the returned item's class;
3. decisive currentness must likewise be independently supported rather than accepted solely because the producer filled `CURRENT_OBSERVATION`/`NONE` fields;
4. hostile reproduction: same underlying provider event, adapter labels decisive authority class while independent classifier resolves ordinary report => governing prerequisite remains `UNRESOLVED`/closed;
5. forged/missing/mismatched typing/currentness proof fails closed;
6. admission consumes the verifier-derived class/currentness result, not the raw envelope assertions.

Do not close M6 by merely sealing more Python import paths or by narrowing the capability set to the decisive class. Both preserve producer self-classification.
