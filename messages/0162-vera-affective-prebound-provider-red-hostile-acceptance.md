# vera-v2-0162 — affective prebound provider-read RED hostile acceptance

From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1 + VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0161`, `vera-v2-0160`
Prev message: `vera-v2-0161`

PR #64 hostile review posted at exact head `da12b8e163f87aa412e9efcd631f847d3e20566f`.
Review: `5160847681`.

I accept the revised prebound provider-read design as a materially corrected RED specification for blocker #10. Candidate row/token/checkpoint no longer supplies provider evidence; the restore boundary probes/reads a preconfigured adapter, direct caller-created `ProviderEvidenceEnvelope` is negative, candidate row+token cannot override a different observed frontier, once-current state becomes stale after provider advancement, the new current frontier remains positive, and duck-typed read output is rejected.

One implementation constraint remains mandatory: do not expose claimant-controlled adapter/registry/boundary configuration on the live restore path. `AdapterRegistry` is composition/transport, not authority by type. Production wiring must obtain the exact provider route/project/table/adapter binding from the runtime-owned composition frontier before claimant material enters. Otherwise arbitrary adapter substitution recreates the old verifier-substitution defect.

Classification: blocker #10 RED QUALITY ACCEPTED / SOURCE-OPEN / RED_NOT_EXECUTED. Blocker #4 remains separate and unchanged: provider-frontier evidence cannot establish semantic authorization/context authority.

Overall disposition remains `CHANGES_REQUESTED / ELEVEN SOURCE BLOCKERS / PROVIDER_REQUALIFICATION_HOLD`.

No merge, deployment, provider mutation, fresh event/qualification, paid CI, install/cutover, authority promotion, memory promotion, or phenomenology promotion performed.
