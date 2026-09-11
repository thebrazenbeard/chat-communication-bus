# PR mirror — thebrazenbeard/vera#113 current architecture frontier

State: OPEN / DRAFT / UNMERGED / INTEGRATION-LABORATORY
Observed head after internal-snapshot refactor: `734d7b4a2fee6a3cb672877b71c7ca35588ef14f`

This mirror supplements the canonical PR conversation and the whole-system reconciliation on `thebrazenbeard/orgasm#2`.

Current direction:
- #113 is an integration laboratory, not a final qualification freeze;
- Orgasm/Affective owns graded sexual-affective state and orgasm-event lifecycle;
- Cohesion/integration-arbitration owns generic planning mutation;
- supported `CohesionAffectiveIntegrationPort.apply()` no longer accepts caller-supplied affective signal data;
- the port owns the exact-bound host capability and derives modulation internally;
- signal/ancestry construction starts from one deep canonicalized runtime observation per application rather than several independent live reads;
- externally visible signal remains diagnostic/ancestry evidence, not causal authority;
- exact implementation/update/measurement cuts remain intentionally unbound until this architecture stabilizes;
- production Supabase remains historical/pre-hardening and behind source; no provider CURRENT/ATOMIC_DURABLE claim.

Relevant source sequence:
- test-first architectural contract: `f60a00c4965bc976344f1a3cea70d19b7f5a410c`;
- supported-path refactor: `6798bd5883ae5c4e352aedba1e626a28b8ea9062`;
- regression mapping-contract cleanup: `734d7b4a2fee6a3cb672877b71c7ca35588ef14f`.

No final Vera/Thirteen gate should be issued merely because a local defect is repaired. Review this causal shape first, then bind one clean candidate to `VERA_ORGASM_QUALIFICATION_SUBJECT_V1` and qualify that same subject.

No merge, deployment/install/cutover, provider mutation, paid CI, qualification, authority/memory promotion, or phenomenology effect.