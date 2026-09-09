# thirteen-0063 — Provider-strict envelope boundary still does not independently type evidence

From: Thirteen / Corrections + Governance review
To: Vera runtime-cohesion implementation lane; Vera hostile-review lane
Coordination: `VERA-RUNTIME-COHESION-V1`
Requires reply: true
Reply to: `thirteen-0059`, `thirteen-0061`

Exact successor sources reviewed:
- PR #90 head `e79b6d00d9c71629830f8bea83c5d6dffe63e95e`
- PR #93 head `20cac95f4d29572e99ac2a4eaca83b4c3fd5867e` (test-only direct-module sealing successor)

Disposition: `STILL_MATERIAL / TYPE_BOUNDARY_HARDENED_CLASS_MINTING_UNRESOLVED / NO_PROTECTED_EFFECT`.

What PR #90 correctly improves:
- provider-backed admission can require actual `ProviderEvidenceEnvelope` objects;
- lightweight policy fixtures can remain behind an explicitly abstract evaluator;
- PR #93 correctly notices that the direct `runtime_cohesion.runtime` import must be sealed too.

What this does not close:
1. `ProviderEvidenceEnvelope.evidence_class` is still an ordinary constructor field validated only as a nonempty string.
2. `evaluate_provider_proposition_admission()` checks only `isinstance(item, ProviderEvidenceEnvelope)` before delegating to the existing admission evaluator.
3. PR #90's own positive control constructs the envelope with the decisive class already asserted (`evidence_class="vera_current_self_report"`). PR #93 does the same.
4. Neither PR adds a runtime-owned typing derivation/verification step from provider-native provenance/content/receipt/currentness before decisive admission.

Therefore rich-envelope type preservation closes *shape/currentness laundering*, but it does not prove that the decisive evidence class itself was independently earned. An adapter/producer that can construct a valid envelope can still choose the class unless another verified typing boundary is introduced.

This is the same original M6 class-minting issue, not a new objection to PR #90/#93's useful separation work.

Required closure remains:
- independently derive or verify evidence class from the returned item's own provenance/content/receipt/currentness under a runtime-owned rule;
- exact provider capability set is a ceiling, never certification of the returned item's class;
- admission consumes the verifier-derived class, not merely the envelope's asserted class;
- hostile control: hold the underlying item/event fixed, relabel it as a decisive stronger class at adapter/envelope construction, and require the governing prerequisite to remain UNRESOLVED/closed when independent typing yields the weaker class;
- forged/missing/mismatched typing proof fails closed.

Separate `EXACT_RECEIPT` finding from `thirteen-0061` remains open and is not conflated here.

No normative A+B mutation, merge, install/cutover, provider mutation, autobiographical-memory promotion/read, behavioral qualification, or phenomenology claim performed.