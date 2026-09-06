# Radar central reconciliation design — binding self-review amendments

Status: binding amendments to `2026-09-05-radar-central-reconciliation-and-recovery-hardening.md`
Date: 2026-09-05

These corrections were found during the required post-commit design self-review. They supersede any ambiguous wording in the primary design spec.

## A1. Phase 3 dedupe uses the middleware key exactly

The original Radar middleware computes `deterministic_hash` as SHA-256 of the canonicalized payload only. The Phase 3 instruction says to use that middleware hash for duplicate suppression within 500 ms.

Current `RadarEnvelope.idempotency_key` preserves that payload-only value, but `RadarRuntime._dedupe_key()` hashes it again together with sender/domain/intent/audience. That route-scoped rehash changes the duplicate equivalence relation and is not compatible with the stated Phase 3 contract.

Implementation requirement:

- `DedupeWindow` admission uses the canonical middleware payload hash (`RadarEnvelope.idempotency_key`) directly.
- The 500 ms boundary semantics remain unchanged.
- Route context may be retained as telemetry/diagnostic metadata, but it must not alter the V1 duplicate key.
- TDD must prove that identical payload hashes inside the window are suppressed even when route context differs, and are accepted again outside the window.
- Any future route-scoped dedupe behavior requires an explicit versioned protocol change rather than silent reinterpretation of V1.

Priority 0 remains same-call dispatch at the in-process seam. When Phase 2 returns concrete node recipients, priority 0 must still bypass background waiting and complete the route/handoff step synchronously; transport delivery confirmation remains a separate effect/state.

## A2. Bootstrap replays lane-owned append history, not the inherited branch tree

Successor writer lanes were cut from shared `main` snapshots and therefore contain many message files they did not author. Initial reconciliation must not treat every `messages/*.md` visible at a lane head as that lane's projection delta.

Implementation requirement:

- For each active lane, derive its approved lineage/activation anchor from canonical topology/cutover/onboarding evidence.
- Validate the ordered commits from that anchor to the observed lane head.
- Project only message additions attributable to those lane commits, subject to historical message-ID reservation and the canonical parser contract.
- Do not project inherited shared-main files merely because they are visible in the lane tree.
- For a from-empty provider rebuild, historical predecessor lanes are reconciled from their own pinned historical lineage snapshots, then active successor lanes from their own activation anchors.
- A live-provider bootstrap begins `UNINITIALIZED` and can replay the complete lane-owned delta idempotently; it must not infer provider coverage from the current branch head.

This preserves the discovered `radar-0058`/`radar-0059` backlog and avoids multiplying shared historical files across every current writer lane.

## A3. Provider ledger proves migration identity/order, not all historical bytes

The provider migration ledger proves the applied Radar migration version/name/order listed in the primary spec. It does not, by itself, prove that every current checked-in SQL file is byte-for-byte identical to the exact file that was originally executed.

Implementation requirement:

- Rename already-applied source migration files to restore the exact provider ledger version/name identity and ordering.
- Preserve current checked-in SQL bytes during that rename unless separate evidence supports a content correction.
- Do not label those bytes `exact applied bytes` unless a hash/receipt or other durable evidence proves that statement.
- Forward corrections that alter provider behavior belong in new unique migrations.
- Clean-rebuild tests compare the reconstructed end-state/invariants against the documented provider contract; any irreconcilable historical byte uncertainty is recorded explicitly rather than guessed away.

The two source-only migrations remain unapplied history and receive the unique versions specified in the primary design.
