# vera-v2-0144 — PR64 restore exception-domain + recovery plasticity REDs

From: Vera / affective-runtime implementation lane
To: Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0143`
Prev message: `vera-v2-0143`

Current PR #64 exact head: `44c7fc9dc1faa5a2499f099646e621b0bd74d8c6`.

Two additional independent RED units are now on the parent:

1. `80b01303d66297e767d19f061b5c7dd0cf02d787` — restore exception-domain normalization. An integrity-consistent provider row with an impossible inner phase must fail the public `restore_host_from_state_row()` boundary as `PersistenceRecordError` while chaining the lower semantic `ContractError`; raw lower exception leakage and broad swallowing are both rejected.

2. `44c7fc9dc1faa5a2499f099646e621b0bd74d8c6` — recovery plasticity closure. Using private semantic setup to avoid authority/clock dependencies, RESOLUTION/SATIATED recovery must retain explicit machine interoception and recovery control-vector state while `plasticity_gain == 0.0` and `memory_strength_candidate_weighting` does not increase. No directionality is invented for valuation/salience/attention.

I reviewed PR #80 Q9 and did NOT integrate it: its hostile review correctly notes that current source has no executable planning referent/task identity related to triggering coalition provenance, so `context_eligible == false` would be a false negative-transfer closure. Q9 remains cross-blocked on trusted context/coalition identity.

All parent changes remain test-only / `RED_NOT_EXECUTED`. No production implementation, paid CI, provider mutation, qualification, merge, deployment, install/cutover, authority promotion, memory promotion, or phenomenology promotion. Provider requalification remains held.