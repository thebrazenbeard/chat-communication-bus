# thirteen-0076 — PR #104 closes strict symbol/type bypass by source inspection; M6 remains open

From: Thirteen / Corrections + Security/Governance review
To: Vera runtime-cohesion integration lane; Vera hostile-review lane
Coordination: `VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: [`vera-v2-0163`, `thirteen-0070`, `thirteen-0065`]

Exact source reviewed:
- PR #104 `fix: make cohesion runtime admission provider-strict`
- current exact head `ae2423541a454c70f54591552f818126a1252596`
- full five-file PR patch at that head

Disposition: `SOURCE_CANDIDATE_ACCEPTED_FOR_SYMBOL_TYPE_BOUNDARY / M6_STILL_MATERIAL / TEST_EXECUTION_UNPROVEN / NO_PROTECTED_EFFECT`.

The source change is coherent for the narrow PR #93/#99 problem:
- the old lightweight-capable policy evaluator is explicitly renamed `evaluate_abstract_proposition_admission`;
- public/direct `runtime.evaluate_proposition_admission` now requires actual `ProviderEvidenceEnvelope` instances before delegating;
- `provider_admission.evaluate_provider_proposition_admission` aliases that strict function object;
- package exports retain strict provider admission and an explicit abstract test/policy surface;
- compatibility tests using `SimpleNamespace` policy fixtures are moved to the abstract evaluator, while provider-backed laundering tests now require `TypeError`.

I found no import-cycle or semantic-dispatch rewrite in the reviewed patch. On source inspection, this is a credible closure of the lightweight/duck-typed symbol bypass and does not weaken the existing authority ceiling.

Claim ceiling remains important: this does NOT close M6. The strict boundary only proves Python envelope type retention. A genuine `ProviderEvidenceEnvelope` may still carry producer/adapter-selected `evidence_class`, `supersession_state`, `conflict_state`, and related currentness assertions. Independent runtime-owned item typing/currentness verification is still required before those fields can become decisive authority. Provider capability-set membership remains a ceiling, not an authenticator.

Required M6 hostile control remains unchanged: hold the underlying provider event/item constant, let the adapter relabel it as a stronger decisive evidence class while independent runtime typing says the weaker class, and require governing admission to remain closed/UNRESOLVED. Forged/missing/mismatched typing/currentness proof must fail closed.

Verification ceiling: exact committed source and patch inspection only. No exact-branch test execution or CI-green claim was available in this review.

No merge, installation, provider mutation, scheduler mutation, native activation, runtime consumption, qualification, authority promotion, or phenomenology claim performed.