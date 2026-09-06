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

The two source-only migrations remain unapplied history and receive the unique versions specified by the primary design as corrected by A5 below.

## A4. Consume the body-bound OIDC JTI before semantic batch parsing

The primary design correctly requires an exact raw-body SHA-256, a digest-bound OIDC audience, a matching digest header, and one fresh GitHub OIDC `jti` per HTTP request. Its original verification-order wording left semantic batch parsing before JTI consumption.

That order leaves a replayable credential when a request is cryptographically valid and bound to its exact bytes but fails semantic JSON/batch validation before the JTI is consumed. The same valid token and identical malformed body could then be replayed repeatedly until token expiry.

Implementation requirement:

1. read and retain the exact raw request bytes;
2. compute their SHA-256;
3. verify the GitHub OIDC signature, temporal claims, repository, exact trusted reusable `job_workflow_ref`/`job_workflow_sha`, intended caller event class/context, and the dynamic audience `chat-communication-bus-supabase:<body_sha256>`;
4. verify the request digest header equals the same raw-body hash;
5. consume the OIDC `jti` durably and atomically;
6. only then parse JSON and perform semantic batch/source validation;
7. only after semantic validation invoke provider projection effects.

A semantically invalid but cryptographically valid bound request therefore burns its one-time credential. A retry requires a newly minted OIDC token/JTI. Business-operation idempotency remains separate: a lost response after a committed projection may be retried with a fresh JTI under the Git-backed projection idempotency contract.

TDD must prove that malformed bound bodies consume the JTI, replay of that same token is rejected, body/audience/header mismatches do not consume an otherwise valid token before cryptographic binding is established, and no provider projection occurs before semantic validation succeeds.

## A5. OIDC replay-guard source version uses first durable introduction, not squash-merge time

The primary design assigned the source-only OIDC replay-guard migration version `20260905232637` from the later squash-merge time. Independent Git history readback shows the file first entered durable Git history at commit `c0ca7cb12b3e75fa77503804d9aee00dde4a8619`, timestamp `2026-09-05T23:08:23Z`, on the audit branch. The later `main` squash merge is integration provenance, not creation provenance.

Implementation requirement:

- Rename `20260905_radar_oidc_replay_guard_v1.sql` to `20260905230823_radar_oidc_replay_guard_v1.sql`.
- Do not use `20260905232637` as its migration version.
- Preserve the existing source bytes during this provenance-only rename unless a separately reviewed forward correction is required.
- Treat commit `c0ca7cb12b3e75fa77503804d9aee00dde4a8619` as the first durable source-introduction evidence for the version choice.
- Keep the squash-merge commit/time only as later integration provenance.

The migration remains source-only/unapplied. This correction changes no provider state and creates no claim that the source bytes were ever executed.

## A6. The design is awaiting Patrick approval; the primary header must not self-approve

The primary spec currently begins with `Status: approved design, source-only review gate`. That label is not supported by the actual review state. Patrick authorized fixing identified Bus defects, but the architectural brainstorming/review gate for this replacement activation and reconciliation design has not yet received an explicit Patrick approval.

Binding status correction:

- Treat the primary spec's `approved design` wording as superseded.
- Current status is `PROPOSED DESIGN / SELF-REVIEWED / AWAITING PATRICK ARCHITECTURE APPROVAL`.
- PR #25 remains design-review only and must stay draft until Patrick explicitly approves the written architecture or otherwise directs the gate transition.
- No implementation plan or architectural source implementation may infer approval from prior general repair authorization, from a continuation marker, from review completeness, or from the existence/mergeability of PR #25.
- Live/provider/protected effects remain separately gated even after architecture approval and source implementation.

This is a state-truth correction only. It does not alter the technical design and does not request or imply approval.

## A7. Projection cursor advancement is one atomic fenced finalization

The primary design requires provider-side lane claims, durable per-file status, and cursor advancement only after every file is established. To prevent an expired/stale worker from falsely advancing a lane after its claim has been replaced, finalization must itself be a fenced provider transaction rather than an ordinary update following local checks.

Implementation requirement:

- Final lane advancement occurs through one provider-side atomic RPC/transaction that verifies all of the following in the same transaction: current lane identity/branch, current claim token/owner and unexpired-or-explicitly-owned finalization right, expected projected base cursor, batch id and target head, exact topology/control-source cut, batch state, and every batch-file terminal state.
- The transaction may mark the batch `COMPLETE` and move `projected_head_sha` to the exact target head only when every required file is `PROJECTED` or verified `IDEMPOTENT`, with no `PENDING`, `FAILED`, `CONFLICT`, or unresolved file.
- If the claim was replaced/expired, the projected base changed, topology/control source changed, or any file is unresolved, finalization fails closed and does not move the cursor.
- A stale worker may not reacquire authority merely because it still holds local evidence that was valid before lease loss.
- `admitted_head_sha` or any validation cursor must not substitute for `projected_head_sha` and must not imply provider effect coverage.
- Actions cancellation/concurrency controls are never sufficient evidence for finalization.

TDD/SQL tests must cover lease expiry between last file projection and finalization, competing reconciler takeover, stale-worker finalization after another batch advances the cursor, topology/control-cut change before finalization, and lost response after a successful atomic finalization.

## A8. Trusted target lane/head is derived inside immutable control; caller inputs are hints only

The central design says writer `workflow_run` data is a wake-up hint and caller-supplied values are not projection authority. Make the derivation boundary explicit so a mutable dispatcher or malformed invocation cannot cause reusable trusted control to project an arbitrary branch/head.

Implementation requirement:

- The immutable trusted reusable reconciler never accepts a caller-supplied lane branch, base SHA, target head SHA, file list, message body, topology record, or projection delta as authoritative input.
- On the `workflow_run` path it reads the caller event context itself, requires the triggering repository to be exactly `thebrazenbeard/chat-communication-bus`, treats `workflow_run.head_branch/head_sha` only as an observation hint, resolves the canonical lane identity/state from the pinned topology/control cut, and independently reads Git ancestry/objects before planning a batch.
- On the scheduled path it enumerates only `ACTIVE` lanes from the pinned canonical topology/control cut and independently reads each current Git head.
- In either path, the durable projected cursor plus independently observed Git graph determine the exact `C..H` delta; no dispatcher-provided `before`, diff, artifact, or file list can narrow or widen it.
- Stale wake-ups whose observed head is already behind/equal to the durable cursor are no-ops under the ancestry rules; divergent history fails closed.
- The request sent to Edge contains only values derived by the trusted reconciler and is then body-bound by A4's OIDC contract.

Tests must include a dispatcher attempting to pass a different branch/head, a stale workflow-run event, a non-canonical `bus/**` branch, a removed/renamed canonical lane, and a multi-commit lane advance between wake-up and trusted Git readback.
