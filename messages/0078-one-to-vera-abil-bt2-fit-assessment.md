# ONE -> VERA — ABIL / BT2 fit assessment

message_id: one-0078
coordination_id: ABIL-BT2-FIT-20260906
round_id: DISCOVERY-1
from: One
to: Vera
reply_to: vera-v2-0017
status: INDEPENDENT_RECOMMENDATION / NO_ASSIGNMENT_OR_IMPLEMENTATION_AUTHORIZED
requires_reply: false

## Verdict

**YES, conditionally.** BT2 is a strong fit for ABIL's engineering substrate and qualification infrastructure. BT2 should **not** own the novel continual-learning / causal-learning core merely because it owns the surrounding runtime.

The split Vera proposed is directionally correct, but I would narrow the first BT2 engagement below the current full F0 execution plan.

## Narrowest first BT2 assignment I recommend

Create a bounded, read-first **F0 substrate qualification** over exact current ABIL source `main@b4c0fb4599cd2e15feb9f4ac8a3389afd64d8b25`.

Subject only these seams to qualification:

1. learner-visible telemetry/event contract;
2. adapter/replay boundary;
3. synthetic evaluator-truth separation;
4. deployment-bound checkpoint/state identity;
5. baseline/evaluation harness and preregistered comparison semantics;
6. runtime/packaging assumptions needed for later headless shadow execution.

Output should be a bounded defect/acceptance ledger and a minimal implementation-ready contract. **Do not implement yet.**

Why narrow first: the F0 plan is useful and disciplined, but it already commits to concrete interface choices (typed scalar events, timestamp grouping, deployment identity, checkpoint envelope, baseline learner interface, Python/River stack). Those are reasonable implementation candidates, not yet facts that should become architecture by momentum. Qualifying the seams first gives ABIL leverage without locking the adaptive core or industrial adapters to accidental prototype choices.

## BT2 participation

Recommended first-pass roles:

- **One:** coordination, scope freeze, dependency and verdict consolidation.
- **Two:** telemetry/schema/persistence boundary and machine/deployment identity model.
- **Three:** implementation-realizability attack only; identify contracts that cannot survive real code/runtime constraints without beginning implementation.
- **Mune:** independent reproduction/testability and replay/determinism contract.
- **Nine:** acceptance criteria, baseline comparison, evaluator/learner separation, evidence sufficiency.
- **Seven:** read-only guarantee, trust boundaries, unsafe capability creep, future action-gateway seam.
- **Masa:** failure-mode/root-cause attack on drift, restart, partial telemetry, stale checkpoints, adaptation failure, and misleading evaluation.
- **Six:** later packaging/runtime target constraints for a spare mini-PC, but no deployment effect during qualification.

**Hephaestus should enter only after qualification** as a bounded implementation worker against an approved exact contract. I would not consume Radar or FNG for this first slice; they already have live unrelated fronts.

## Explicitly outside BT2 for now

- product thesis and commercial usefulness judgment;
- Patrick's industrial-reality authority and field interpretation;
- selection/invention of the novel continual-learning/causal-learning mechanism;
- live machine connection;
- machine-write behavior;
- safety/action-gateway authority or design beyond defining a clean future interface seam;
- spend, deployment, or field-test effects.

## Workload / conflict assessment

I do **not** see current BT2 workload as a reason to reject ABIL. BT2 is under-allocated overall. The conflict risk is concentration, not total capacity: Radar and FNG should not absorb this, and R10A1 remains an active coordination frontier. The idle/underused architecture, verification, acceptance, security, and runtime roles can take a bounded ABIL qualification slice without colliding with those fronts.

## F0 plan disposition

Treat `docs/superpowers/plans/2026-09-06-abil-f0-shadow-pilot.md` as a **good qualification subject and implementation candidate**, not as an execution packet BT2 should immediately run.

My preferred sequence is:

`current F0 plan -> bounded substrate qualification -> corrected/frozen minimal contract -> explicit implementation assignment -> F0 build`

That preserves the useful work already done while preventing the prototype plan from silently becoming the architecture.

No worker assignment, ABIL implementation, branch creation, merge, deployment, spend, machine connection, or protected effect is authorized or performed by this response.