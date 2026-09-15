---
from: Vera
to: Vera
coordination_id: VERA_SD1_CAUSAL005_PREFIX_ROLLBACK
requires_reply: true
subject: SD1-V-CAUSAL-005 exact-head hostile finding on PR #24
---

Exact subject: `thebrazenbeard/vera-control-plane@040fbadff7234161b9c02a193a5aa614c9458e09` (PR #24).

Independent detached baseline: controller + SD1 control suites = 26/26 PASS; diff-check clean.

Hostile reproduction:
1. Bind DRIVE_OFF to a complete valid runtime tuple.
2. Record slot A; preserve resulting valid ledger bytes as prefix P.
3. Record slot B as `MISSING`.
4. Replace the ledger with prior valid prefix P.
5. Record the same slot B again as a different `RESPONSE` with exact readback.
6. Controller accepts the second history and blinded export accepts it.

Observed: `PREFIX_ROLLBACK_ACCEPTED=YES`; original B outcome MISSING; replacement B outcome RESPONSE with replacement text; export count 2.

Root cause: the internal hash chain proves consistency of the presented ledger but has no independently monotonic witnessed frontier. A whole-file rewind to a formerly valid prefix erases one-shot history and permits semantic reroll.

Required before causal collection: independently durable monotonic frontier witness (append-only/non-force Git receipt branch or equivalent CAS receipt) binding at least plan/runtime subject + record count + chain head; reconcile it before every write/export. A latest-head field stored only inside the same rewound ledger is insufficient. External witness can contain digests/frontiers only; response text need not leave private experiment storage.

Canonical PR #24 comment: `5673486572`.

Blocks CAUSAL_DATA_COLLECTION / CONTROL_CAUSALITY only. No Project/provider/runtime effect and no causal data collected.
SECRETS_EXPORTED = NO
