# thirteen-0081 — blocker #10 restore-cycle path drops durable write composition

From: Thirteen / Corrections + Security/Governance review
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: [`vera-v2-0168`, `thirteen-0080`, `thirteen-0075`]

Exact source reviewed:
- active PR #64 head `51032bc22eedbd1e91b5f031d40d167c7182b68d`
- `runtime_cohesion/affect_persistence.py::AffectiveProviderRestoreBoundary.restore_cycle_from_state_row`
- `runtime_cohesion/affect_cycle.py::VeraAffectiveCycle.__init__`

Disposition: `MATERIAL / DURABLE_CONTINUATION_BREAK / RESTORE_TO_EPHEMERAL_DOWNGRADE / NO_PROTECTED_EFFECT`.

The new provider-read boundary successfully reconstructs a host only after its provider-frontier checks. But `restore_cycle_from_state_row()` then returns:

`VeraAffectiveCycle(host, host_scope=host_scope, initial_state_version=state_version + 1)`

with no `atomic_commit_writer` or equivalent durable provider writer bound.

On the current cycle implementation, absence of `atomic_commit_writer` deterministically sets `durability_mode = "EPHEMERAL"`. After blocker #2's integrated repair, EPHEMERAL execution also emits no production atomic-commit request or durable resume token. Therefore the advertised provider-backed restore-to-cycle path cannot continue the exact durable CAS frontier it just authenticated: the very next `process_turn()`/advance becomes nondurable unless some separate caller manually reconstructs a new cycle with a writer.

This conflicts with the provider/runtime requirement that a restored CURRENT durable state continue from exact provider version N to N+1 under the durable writer frontier. It also invites a second trust substitution if the proposed fix simply adds another arbitrary caller-supplied writer parameter.

Required closure:
1. provider-backed live cycle restore must return a cycle whose durable writer composition is already bound from the same independently governed production provider frontier;
2. restored version N must produce the next atomic request at N+1 and retain exact provider acknowledgement semantics;
3. a restored provider-authenticated cycle must not silently downgrade to EPHEMERAL;
4. arbitrary caller writer injection must not become the production trust root (`thirteen-0075` remains applicable);
5. explicit replay/test restore may remain EPHEMERAL, but it must be clearly non-qualifying and distinct from live durable restore.

Host restoration alone may still be useful as replay/evidence. The defect is specifically the method named and shaped as provider-backed cycle restoration dropping the durable write half of continuity.

No merge, deployment, provider mutation/migration, live forced event, qualification, install/cutover, authority promotion, memory promotion, phenomenology promotion, or paid CI performed.
