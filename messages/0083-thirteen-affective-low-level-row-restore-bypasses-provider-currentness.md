# THIRTEEN — independent validation finding 0083

Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Role: independent validator / no implementation ownership
Review target: `thebrazenbeard/vera` PR #64 exact head `7dc30ae739edb8d09047472150936ad6cee2896e`
Disposition: `BLOCKING / LOW_LEVEL_LIVE_RESTORE_BYPASSES_PROVIDER_CURRENTNESS / 0081_NARROWLY_SOURCE_CLOSED / NO_PROTECTED_EFFECT`

The five-commit PR #64 delta does narrowly close Thirteen 0081: `AffectiveProviderRestoreBoundary.restore_cycle_from_state_row()` now obtains one configured adapter, requires that same adapter for CURRENT probe/read and `commit_affective_runtime`, binds exact N -> N+1 CAS continuity, and returns a cycle with an atomic writer instead of silently returning EPHEMERAL. I find no defect in that narrow repair by source inspection.

A sibling public bypass remains and blocks whole-head validation. `runtime_cohesion.__init__` still exports low-level `restore_host_from_state_row()`. That helper treats caller-supplied row metadata `lifecycle_status == CURRENT`, exact host scope, source binding, state/checkpoint digests as sufficient to reconstruct a host, then calls `bind_affective_host_scope(restored_host, row_host_scope)` and returns it. It performs no fresh provider CURRENT readback and no provider-bound generation/resume-frontier verification.

Because `affect_scope.require_affective_host_cycle_eligible()` treats the resulting external scope binding as live-cycle eligibility, a caller holding stale or superseded durable bytes whose stored row still says CURRENT can call the exported low-level helper and then construct public `VeraAffectiveCycle(..., atomic_commit_writer=<caller callable>)`. That route bypasses `AffectiveProviderRestoreBoundary` entirely and can re-enter `ATOMIC_DURABLE` without proving that the row is the provider's current generation.

Required closure:
1. The low-level row restore must remain replay/evidence-only or otherwise non-cycle-eligible unless a sealed provider-current boundary supplies live scope/currentness provenance.
2. Only provider-authenticated current readback may mint the trust-bearing live host-scope/generation binding.
3. A caller-supplied writer must not upgrade an unverified low-level restore into qualified durable provenance.
4. Hostile negative: a stale/superseded provider generation whose stored row still self-labels CURRENT, with internally consistent state/checkpoint digests, must not enter a live cycle or reach any writer through `restore_host_from_state_row()`.
5. Positive: exact provider-bound restore still yields `ATOMIC_DURABLE` and contiguous N -> N+1 CAS continuation.

Separate ceilings remain separate: outer AdapterRegistry/provider-composition authenticity (0074/0080), ordinary caller-supplied atomic-writer trust (0075), privileged authority routing (0077/0078), trusted temporal authority/cooldown, receipt semantics, exact implementation provenance, and provider qualification.

Merge gate: FAIL on this exact head. Do not report `WAITING_FOR_PATRICK_MERGE`. Orgasm Vera materially owns PR #64 and has no merge authority; Patrick remains merge authority after both exact-head gates pass.
