# Radar projection journal V1

Status: source contract; provider migration not applied.

Radar reconciles each ACTIVE writer lane against a durable provider cursor without treating a writer branch or caller-supplied head as authority.

The journal has three durable state surfaces: lane state (`identity_id`, `branch`, `projected_head_sha`, trusted control/topology cut), one claimed reconciliation batch, and per-file projection results.

Authority rules:

- lane state must be seeded explicitly; claiming work cannot create or invent a cursor;
- an uninitialized live bootstrap is represented by an explicitly seeded `NULL` projected cursor;
- control/topology cut state is lane-scoped and must match the batch at claim and finalization;
- one live claim exists per lane; an expired claim may be replaced and its old token is permanently fenced;
- a file result is successful only as `PROJECTED` or verified `IDEMPOTENT`; `FAILED`, `CONFLICT`, and `PENDING` never permit cursor advancement;
- finalization is one provider transaction that validates claim token/lease, expected base cursor, control/topology cut, batch target, and all file states before atomically marking the batch COMPLETE and advancing the cursor;
- replay of a successful finalization is idempotent only when the durable lane cursor still equals the completed batch target;
- `service_role` may read journal state and execute journal RPCs but has no direct table-write grant, so the fenced state transitions are not bypassable through ordinary table DML.

Trusted Git derivation is separate from the journal. For a current ACTIVE lane, the reconciler obtains the branch from canonical topology, the activation anchor from cutover/onboarding evidence, the observed head and ancestry from the trusted Git object database, and the projected cursor from the journal. The resulting dispositions are `NOOP`, `FORWARD`, `STALE_EVENT`, or `DIVERGED_HISTORY`; divergence fails closed.

Writer branch files are inert Git data. The trusted reconciler does not import or execute code from a writer branch.

Provider deployment, migration application, workflow activation, and live cursor bootstrap remain separately authorized effects.
