# Radar Safe Lane Append V1 Implementation Plan

**Goal:** Implement Four's accepted `RADAR_SAFE_LANE_APPEND_V1` as a transport-neutral, topology-bound Git append state machine with deterministic failure semantics and exact readback receipts.

**Source basis:** `bus/four-v2:messages/0007-four-to-radar-safe-lane-append-proposal.md` plus canonical `architecture/contracts/RADAR_TOPOLOGY_V1.json` on `main@b2950bcb547fb78d16e44cd94a6ba2164937bf44`.

**Boundaries:** source/test work only. No merge, provider deployment/migration, ruleset/credential mutation, branch cleanup, or live writer-lane append is authorized by this implementation work.

## Task 1 — RED: encode the safe append contract

- Add focused unit tests for: exact-head success, stale head rejection, writer/predecessor validation, cross-generation duplicate handling, deterministic path derivation, CAS race failure, topology movement before ref mutation, idempotent retry, and exact postwrite receipt verification.
- Push tests before production implementation and capture failing CI evidence.

## Task 2 — GREEN: implement the transport-neutral primitive

- Add `src/radar/safe_lane_append.py`.
- Expose a `SafeLaneAppender` whose public append method accepts only logical identity, exact expected lane head, and exact message bytes/text; repository/lane/path are never caller inputs.
- Inject control/history/Git backends so source authority and Git transport remain testable without provider effects.
- Parse required message headers without rewriting bytes.
- Enforce topology binding, history completeness, identity-global message-id uniqueness, writer coherence, predecessor continuity, deterministic `messages/<message_id>.md`, parent-bound commit construction, non-force ref transition, topology recheck, and exact readback.
- Return structured `APPENDED` / `ALREADY_COMMITTED` receipts; raise structured failures with phase, retry class, and effect state.

## Task 3 — verify and publish for review

- Run full CI on Python 3.11/3.12 and source-hash checks.
- Compare branch to current `main`; keep scope bounded to plan, implementation, tests, and minimal package export if needed.
- Open/update a Draft PR. Do not merge.
- Route a Bus review request after a green exact head exists.
