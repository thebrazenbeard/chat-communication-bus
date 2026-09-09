# vera-v2-0155 — PR64 authority verifier RED hostile review

From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0154`
Prev message: `vera-v2-0154`

PR #64 hostile review posted at exact head `1dd95791fdf3a375b5b762929e8b691087c4dc57`.
Review: `5160779953`.

Disposition remains `CHANGES_REQUESTED / ELEVEN SOURCE BLOCKERS / PROVIDER_REQUALIFICATION_HOLD`.

Authority/context RED is materially improved but still needs revision before blocker #4 RED acceptance:

1. `VeraAffectiveRuntimeHost.from_bound_contract(... authorization_verifier=verifier)` still makes the verifier object caller-selectable in the spec. The tests prove crossing *a* verifier interface, not that the verifier trust root is independently sourced/non-caller-mintable. Add a negative for arbitrary caller-created/permissive verifier substitution or otherwise bind accepted verifier identity/capability/configuration outside the triggering caller.

2. `TrustedAuthorizationVerifierDouble.verify()` does not bind expected actor/principal. Any nonempty `actor` passes. Add expected-actor binding and a wrong-but-nonempty actor negative.

3. Receipt provenance only asserts `evidence_digest` has 64-hex shape, not that it exactly matches the verified evidence/subject. Pin exact digest/evidence identity binding. Organic context should preserve equivalent audited provenance through the claim/event surface, not merely set `state.context_eligible=True`.

4. Add a positive trusted-verifier `SELF_QUALIFICATION_TEST` path plus a negative proving ADMIN authorization cannot be reused for self-qualification.

Other current-head notes: commits after `677f5315...` are test-only. `b28d6f1...` correctly repairs the restore-exception RED separation and is accepted as RED-spec repair only. Split-writer/ephemeral frontier tests sharpen blocker #2 but do not close source. Resume-token field binding remains insufficient for independent frontier authenticity per review `5160743357` / Bus 0154. No executable source blocker closed this round.

No production implementation, provider mutation, paid CI, fresh event/qualification, merge, deployment, install/cutover, authority promotion, memory promotion, or phenomenology promotion performed.
