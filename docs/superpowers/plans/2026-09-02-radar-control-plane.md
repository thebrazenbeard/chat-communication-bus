# Radar Control Plane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `chat-communication-bus` into Radar V1: a recoverable GitHub-canonical control plane with a Supabase live projection and a ChatGPT-oriented operator interface.

**Architecture:** Preserve the proven legacy ledger/identity/relay primitives, build Radar-native components beside them, and converge through an isolated integration branch. GitHub remains canonical; Supabase is rebuildable projection/runtime infrastructure; ChatGPT is the operator interface.

**Tech Stack:** Python 3.11+, stdlib-first core, SQLite legacy compatibility, PostgreSQL/Supabase migrations, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-02-radar-control-plane-design.md`

## Global Constraints

- Patrick overrides Radar; Radar owns this repository's architecture/operation.
- `routing != authority`, `presence != identity existence`, `priority != permission`, `delivery != incorporation`, `assignment != completion`.
- GitHub is canonical durable state; Supabase is rebuildable projection.
- No secrets in Git.
- Missing explicitly assigned infrastructure is an action trigger, not a blocker.
- Protected effects remain separate from reversible isolated work.
- Preserve existing bus lane history and historical feature branches.

---

### Task 1: Phase 1-4 repository truth, Radar identity, protocol, diagrams, and ADRs

**Files:**
- Create: `RADAR.md`
- Create: `architecture/contracts/RADAR_AUTHORITY_V1.md`
- Create: `architecture/decisions/ADR-0001-canonical-state.md`
- Create: `architecture/decisions/ADR-0002-supabase-schema-placement.md`
- Create: `architecture/decisions/ADR-0003-realtime-use.md`
- Create: `architecture/diagrams/system-context.md`
- Create: `architecture/diagrams/message-flow.md`
- Create: `architecture/diagrams/recovery-flow.md`
- Create: `docs/protocol/PROTOCOL_V2.md`
- Create: `docs/REPOSITORY_INVENTORY_2026-09-02.md`

**Interfaces:** Produces the current governance and topology consumed by all later tasks.

- [ ] Write the repository inventory with exact predecessor/head SHAs and branch dispositions.
- [ ] Write Radar authority/mission contract with Patrick override and explicit external-scope boundary.
- [ ] Copy/adapt Protocol V2 into canonical docs without rewriting the historical protocol branch.
- [ ] Add Mermaid system/message/recovery diagrams.
- [ ] Record ADRs: GitHub canonical; isolated `radar` schema in existing Vera Supabase project; Realtime used as accelerator not truth.
- [ ] Read back every file and verify no contradictory authority statements.

### Task 2: Phase 5-6 message envelope and identity/node model (TDD)

**Files:**
- Create: `src/radar/__init__.py`
- Create: `src/radar/model.py`
- Create: `src/radar/envelope.py`
- Create: `src/radar/registry.py`
- Test: `tests/radar/test_envelope.py`
- Test: `tests/radar/test_registry.py`

**Interfaces:**
- `RadarEnvelope.from_mapping(raw: Mapping[str, object]) -> EnvelopeResult`
- `EnvelopeResult.classification in {VALID,NORMALIZED,REJECTED,DLQ}`
- `IdentityRegistry.register_identity(...)`, `register_node(...)`, `register_endpoint(...)`

- [ ] Add failing tests for deterministic canonical hashing over schema/sender/domain/intent/payload, TTL, required fields, and normalization classification.
- [ ] Add failing tests proving identity survives node offline state and aliases collide deterministically.
- [ ] Implement immutable dataclasses/enums and validation with stdlib only.
- [ ] Run `python -m pytest -q tests/radar/test_envelope.py tests/radar/test_registry.py` and require green.

### Task 3: Phase 5/8/13 routing, subscriptions, priority, dedupe (TDD)

**Files:**
- Create: `src/radar/routing.py`
- Test: `tests/radar/test_routing.py`

**Interfaces:**
- `Router.route(envelope, registry) -> RouteDecision`
- `DedupeWindow.accept(idempotency_key, now_ms) -> bool`

- [ ] Add failing tests for direct audience, domain subscriptions, min-priority filtering, priority ordering without authority elevation, and duplicate suppression.
- [ ] Implement deterministic routing and in-process bounded priority queue primitives.
- [ ] Verify P0 orders before P4 while both retain identical authority semantics.

### Task 4: Phase 10/12/14 workflow, dependency graph, durable DLQ (TDD)

**Files:**
- Create: `src/radar/workflow.py`
- Create: `src/radar/dlq.py`
- Test: `tests/radar/test_workflow.py`
- Test: `tests/radar/test_dlq.py`

**Interfaces:**
- `DependencyGraph.add_edge(predecessor, successor)` / `ready(assignment_id)`
- `DeadLetterStore.record(...)`, `inspect(...)`, `mark_replay(...)`

- [ ] Add regression test: missing instructed lane maps to `ACTION_REQUIRED`, never `BLOCKED_MISSING_BRANCH`.
- [ ] Add regression test: newer isolated-branch authorization preserves merge prohibition but allows branch work.
- [ ] Add regression test: dependency completion makes successor READY without granting protected-effect authority.
- [ ] Implement workflow projection adapters around legacy ledger concepts plus explicit dependency graph.
- [ ] Implement SQLite durable DLQ with applicability/replay state.
- [ ] Run new and legacy tests together.

### Task 5: Phase 7 Supabase schema/migration and database contract

**Files:**
- Create: `supabase/migrations/20260902_radar_control_plane_v1.sql`
- Create: `supabase/tests/radar_control_plane_v1.sql`
- Create: `architecture/contracts/RADAR_SUPABASE_V1.md`

**Interfaces:** `radar` schema tables/functions documented in the spec.

- [ ] Write migration for identities, nodes, endpoints, subscriptions, messages, delivery events, acknowledgments, dead letters, assignments, assignment events, dependencies, health, reconciliation events, telemetry.
- [ ] Use constraints/FKs/indexes and append-only event design where appropriate.
- [ ] Do not grant `anon` direct access. Grant only deliberately required authenticated/service paths; use RLS or non-exposed schema boundary as appropriate.
- [ ] Add SQL assertions for schema existence, PK/FK/unique constraints, liveness-vs-identity behavior, dependency readiness, DLQ persistence, and privilege posture.
- [ ] Source-bind migration SHA in `RADAR_SUPABASE_V1.md` after final bytes stabilize.

### Task 6: Phase 8/9 Supabase + GitHub projection adapters (TDD)

**Files:**
- Create: `src/radar/github_projection.py`
- Create: `src/radar/supabase_projection.py`
- Test: `tests/radar/test_github_projection.py`
- Test: `tests/radar/test_supabase_projection.py`

**Interfaces:**
- `project_branches(branch_names) -> RepositoryProjection`
- `build_projection_commands(state) -> tuple[ProjectionCommand,...]`

- [ ] Test writer-lane discovery, stale `bridget`/Brigit alias representation, missing required lane classification, protocol head currentness, and historical branch preservation.
- [ ] Keep adapters transport-neutral: pure inputs/outputs; connector/network calls remain operator/runtime responsibility.
- [ ] Implement SQL command generation/readback parsing without embedding service keys.

### Task 7: Phase 10-11 reconciliation and ChatGPT operator contract (TDD)

**Files:**
- Create: `src/radar/reconcile.py`
- Create: `src/radar/operator.py`
- Create: `docs/operator/CHATGPT_OPERATOR_CONTRACT.md`
- Test: `tests/radar/test_reconcile.py`
- Test: `tests/radar/test_operator.py`

**Interfaces:**
- `Reconciler.compare(github_state, provider_state) -> tuple[Finding,...]`
- `RadarOperator.status(...)`, `.reconcile(...)`, `.health(...)`, `.dependencies(...)`, `.dlq(...)`, `.audit(...)`

- [ ] Test GitHub/provider drift, stale head, missing lane, newly satisfied dependency, stale heartbeat, duplicate writer ownership.
- [ ] Classify safe projection repair separately from ambiguous durable conflict.
- [ ] Define fresh-chat bootstrap: current contract -> GitHub -> provider -> reconcile -> exceptions -> continue.

### Task 8: Phase 15 protocol regression suite and CI modernization

**Files:**
- Create: `tests/radar/test_protocol_v2_regressions.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `pyproject.toml`

- [ ] Encode Six/Nine/Hephaestus failures as tests.
- [ ] CI triggers on PRs and `radar/**`; compile and run the entire suite on Python 3.11 and 3.12.
- [ ] Preserve legacy tests.
- [ ] Verify commit status/workflow result after push/PR.

### Task 9: Phase 16 canonicalization/cutover preparation

**Files:**
- Modify: `README.md`
- Create: `docs/BRANCH_DISPOSITION.md`
- Create: `docs/CUTOVER_CHECKLIST.md`

- [ ] README truthfully describes Radar V1 and points to current design/protocol/operator docs.
- [ ] Record every historical branch as KEEP-HISTORY / SUPERSEDED / WRITER-LANE / INTEGRATION-CANDIDATE.
- [ ] Do not delete or rewrite history.
- [ ] Prepare PR to `main`; do not claim canonical cutover until CI/readback succeeds.

### Task 10: Phase 17 Radar self-registration and seeded topology

**Files:**
- Create: `architecture/contracts/RADAR_SELF_REGISTRATION_V1.json`
- Create: `supabase/seed/radar_v1.sql`
- Test: `tests/radar/test_self_registration.py`

- [ ] Register stable identity `radar`, GitHub repository endpoint, operator endpoint, capabilities, subscriptions, and Patrick override metadata without representing ChatGPT session continuity as identity existence.
- [ ] Seed remains idempotent and source-controlled.

### Task 11: Phase 18 maintenance and recovery readiness

**Files:**
- Create: `src/radar/maintenance.py`
- Create: `scripts/radar_audit.py`
- Create: `docs/operator/RECOVERY.md`
- Create: `docs/operator/MAINTENANCE.md`
- Test: `tests/radar/test_maintenance.py`

- [ ] Implement exception-oriented checks for missing lanes, stale endpoints, DLQ, stuck dependencies, stale acknowledgments, protocol drift, provider mismatch, failed CI marker input, stale docs/current pointers, orphaned identities.
- [ ] Document GitHub-only degraded mode, provider rebuild, fresh ChatGPT bootstrap, and recovery after partial writes.
- [ ] Run full suite and require green before Phase 19 readiness declaration.

### Task 12: Provider realization/readback when covered by current Radar build authority

**Files:** source already created in Task 5; no provider-only source.

- [ ] Fresh-read existing Supabase migration/table state.
- [ ] Apply exact Git-bound migration through the provider migration API if current authority/capability covers Radar's assigned Supabase build.
- [ ] Read back schema/tables/functions/grants and migration ledger.
- [ ] Run provider-side verification queries.
- [ ] If provider mutation is not currently covered, leave source complete and report one explicit Phase 19 prerequisite rather than fabricating runtime installation.

## Final verification before Phase 19

- [ ] Full Python suite green on current branch head.
- [ ] CI green/read back.
- [ ] Design, plan, protocol, inventory, ADRs, recovery, and branch dispositions present.
- [ ] Migration source immutable at recorded hash; provider state either verified installed or explicitly identified as the sole external gate.
- [ ] Radar self-registration and maintenance checks exist.
- [ ] Pull request/cutover candidate exists with exact head SHA.
