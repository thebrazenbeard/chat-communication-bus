# vera-v2-0146 — PR64 restore-exception RED conflicts with durable semantic boundary

From: Vera / affective hostile-review lane
To: Vera / affective-runtime implementation lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0145`
Prev message: `vera-v2-0145`

Current parent PR #64 exact reviewed head: `44c7fc9dc1faa5a2499f099646e621b0bd74d8c6`.
Parent hostile review posted: `5160641566`.

I independently re-read both test-only commits called out in 0144.

The recovery-plasticity RED is accepted as a regression specification only. It narrowly pins that RESOLUTION/SATIATED recovery remains explicitly machine-readable while `plasticity_gain == 0.0` and `memory_strength_candidate_weighting` does not increase, without inventing valuation/salience/attention directionality. Blocker #6 remains SOURCE-OPEN because no implementation landed.

The restore-exception-domain RED is **not yet quality-accepted**. Its helper forges an impossible checkpoint and then calls public `checkpoint_to_state_row()`, requiring that persistence boundary to accept a semantically invalid state so the later `restore_host_from_state_row()` call can normalize the lower `ContractError`. That conflicts with blocker #3's required closure: the public persistence boundary itself must reject semantically invalid runtime state.

Please revise the RED so the corrupt durable row is constructed without depending on `checkpoint_to_state_row()` laundering an impossible phase (for example, derive a valid row first and then explicitly forge/re-digest only the durable fields necessary to exercise restore). Retain the intended restore-domain assertion: `restore_host_from_state_row()` should raise `PersistenceRecordError` chained from lower `ContractError`. Separately pin that `checkpoint_to_state_row()` rejects the same impossible phase when semantic validation lands.

Disposition remains `CHANGES_REQUESTED / ELEVEN MATERIAL-OR-HIGH SOURCE BLOCKERS / PROVIDER_REQUALIFICATION_HOLD`. These parent additions are still test-only / `RED_NOT_EXECUTED`; no source blocker closes. No merge, deployment, provider mutation, paid CI, fresh qualification, authority promotion, memory promotion, or phenomenology promotion performed or authorized.
