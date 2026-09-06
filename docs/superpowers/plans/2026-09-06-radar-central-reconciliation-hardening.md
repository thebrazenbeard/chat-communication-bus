# Radar Central Reconciliation Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved Radar architecture so writer branches are inert Git evidence, reconciliation is centrally trusted and journaled, routing is node-granular, parser/recovery contracts converge, and the source tree is reproducible and provider-ready without performing live provider effects.

**Architecture:** Preserve GitHub as canonical message evidence. A default-branch dispatcher wakes an immutable trusted reconciler, which independently derives ACTIVE lane/head/delta, validates canonical message bytes, records durable batch/file progress, and emits body-bound GitHub OIDC requests. Provider SQL remains source-only until separately authorized; every cursor advance is fenced and atomic with batch completion.

**Tech Stack:** Python 3.11/3.12, pytest, PostgreSQL/Supabase SQL, GitHub Actions YAML, TypeScript/Deno Edge Function source, JSON contracts/fixtures.

**Spec:** `docs/superpowers/specs/2026-09-05-radar-central-reconciliation-and-recovery-hardening.md` plus binding amendments in `docs/superpowers/specs/2026-09-05-radar-central-reconciliation-self-review-amendments.md`.

## Global Constraints

- Source-only implementation; do not deploy Supabase migrations or Edge Functions.
- Do not merge to `main`, mutate repository rules/settings, credentials, or branch protection.
- Phase 1 taxonomy remains strict and unknown tags remain DLQ.
- Phase 3 duplicate suppression uses `RadarEnvelope.idempotency_key` exactly with a 500 ms window.
- Priority 0 remains same-call dispatch at the in-process seam.
- Heartbeat cadence remains 60,000 ms with `domain=system`, `intent=telemetry`, priority 4.
- Only topology records with lifecycle `ACTIVE` are projection/routing-current; registered-but-gated lanes are inert.
- Cursor advancement requires one fenced provider transaction that also marks the batch COMPLETE after every file reaches terminal `PROJECTED` or `IDEMPOTENT` state.
- Dispatcher/workflow inputs are hints only; trusted reconciliation independently derives lane, head, ancestry, and delta.
- OIDC raw-body binding must consume JTI only after cryptographic body/audience/header binding and before semantic JSON parsing.
- OIDC replay-guard source migration version is `20260905230823`.

---

### Task 1: Restore migration identity/order and SQL assertion truth

**Files:**
- Rename the eight applied Radar migrations to their provider-ledger timestamps.
- Rename `supabase/migrations/20260903_radar_thread_closure_v1.sql` to `supabase/migrations/20260903214334_radar_thread_closure_v1.sql`.
- Rename `supabase/migrations/20260905_radar_oidc_replay_guard_v1.sql` to `supabase/migrations/20260905230823_radar_oidc_replay_guard_v1.sql`.
- Modify `supabase/tests/radar_realtime_v1.sql`.
- Add `tests/radar/test_migration_chain_contract.py`.

**Interfaces:**
- Consumes: provider-ledger order recorded in the approved spec.
- Produces: unique lexicographically correct migration chain and executable Realtime assertion SQL.

- [ ] **Step 1: Write the failing migration-chain test**

```python
from pathlib import Path

EXPECTED = [
    "20260902120716_radar_control_plane_v1.sql",
    "20260902120826_radar_realtime_v1.sql",
    "20260902203610_radar_visual_identity_v1.sql",
    "20260902204759_radar_live_message_projection_v1.sql",
    "20260902231445_radar_live_message_collision_v1.sql",
    "20260903000603_radar_receipt_plane_v1.sql",
    "20260903001906_radar_assignment_plane_v1.sql",
    "20260903113314_radar_operator_views_v1.sql",
    "20260903214334_radar_thread_closure_v1.sql",
    "20260905230823_radar_oidc_replay_guard_v1.sql",
]

def test_radar_migration_versions_are_unique_and_ordered():
    names = sorted(p.name for p in Path("supabase/migrations").glob("*_radar_*.sql"))
    assert names == EXPECTED
    assert len({name.split("_", 1)[0] for name in names}) == len(names)
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest -q tests/radar/test_migration_chain_contract.py`
Expected: FAIL because current filenames collapse provider versions.

- [ ] **Step 3: Rename without changing bytes**

Use Git tree moves preserving the existing blobs exactly. Do not edit historical SQL while renaming.

- [ ] **Step 4: Fix Realtime assertion ambiguity and expected publication set**

Replace the ambiguous catalog filter with an explicit alias:

```sql
FROM pg_publication_tables AS ppt
WHERE ppt.pubname = 'supabase_realtime'
  AND ppt.schemaname = 'radar'
```

Assert the intentional current set:
`acknowledgements, assignments, dependencies, identity_visuals, messages, nodes, reconciliation_events`.

- [ ] **Step 5: Verify GREEN**

Run: `python -m pytest -q tests/radar/test_migration_chain_contract.py`
Expected: PASS.

- [ ] **Step 6: Commit**

Commit: `fix: restore Radar migration provenance order`.

---

### Task 2: Canonical message grammar and shared conformance fixtures

**Files:**
- Create `docs/protocol/BUS_MESSAGE_GRAMMAR_V1.json`.
- Create `tests/fixtures/bus_message_grammar_v1.json`.
- Create `src/radar/message_grammar.py`.
- Modify `src/radar/writer_lanes.py` to call the canonical parser for admission headers.
- Modify `src/radar/bus_message_projection.py` to call the same parser.
- Add `tests/radar/test_message_grammar.py`.
- Extend Edge tests/artifact checks to verify the TypeScript parser accepts/rejects the same fixtures.

**Interfaces:**
- Produces: `parse_bus_message(content: bytes, path: str = "<memory>") -> ParsedBusMessage` and `parse_bus_bool(value: str) -> bool`.

- [ ] **Step 1: Add RED fixtures**

Fixtures must include: duplicate normalized header; invalid `requires_reply: maybe`; valid `true/false/yes/no/1/0` only if the grammar explicitly admits each lexeme; timezone-less non-date timestamp rejection; frontmatter scalar-only behavior; body-terminal `#ENDTHREAD`; UTF-8 failure; writer/message-id normalization.

- [ ] **Step 2: Add parser tests**

```python
def test_invalid_boolean_rejected_before_git_admission():
    with pytest.raises(MessageGrammarError, match="INVALID_BOOLEAN"):
        parse_bus_message(b"message_id: radar-9999\nwriter: Radar\nrequires_reply: maybe\n\nbody\n")
```

- [ ] **Step 3: Verify RED**

Run: `python -m pytest -q tests/radar/test_message_grammar.py tests/radar/test_writer_lanes.py tests/radar/test_bus_message_projection.py`
Expected: new grammar tests fail because no shared parser exists.

- [ ] **Step 4: Implement canonical parser and adapters**

`ParsedBusMessage` must expose normalized `headers`, `body`, `full_sha256`, `body_sha256`, `message_id`, `writer`, `requires_reply`, `requires_ack`, and normalized timestamp.

- [ ] **Step 5: Verify GREEN**

Run the same pytest command; expected PASS.

- [ ] **Step 6: Commit**

Commit: `feat: add canonical Bus message grammar`.

---

### Task 3: Topology lifecycle and Parallax currentness

**Files:**
- Modify `architecture/contracts/RADAR_TOPOLOGY_V1.json`.
- Modify `src/radar/writer_lanes.py`.
- Modify Parallax onboarding/currentness contract and `tests/radar/test_topology_contract.py`.
- Add `tests/radar/test_writer_lane_lifecycle.py`.

**Interfaces:**
- Extend `WriterLane` with `lifecycle: str`.
- `load_writer_lanes(..., active_only: bool = True)` defaults to ACTIVE-only routing/projector view.
- `load_registered_writer_lanes(...)` exposes all registry entries for bootstrap/onboarding tooling.

- [ ] **Step 1: RED tests**

```python
def test_registered_inert_lane_is_not_current_writer_lane(tmp_path):
    topology = write_topology(tmp_path, lifecycle="REGISTERED_INERT")
    assert load_writer_lanes(topology) == {}
    assert load_registered_writer_lanes(topology)["parallax"].lifecycle == "REGISTERED_INERT"
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest -q tests/radar/test_topology_contract.py tests/radar/test_writer_lane_lifecycle.py tests/radar/test_writer_lanes.py`

- [ ] **Step 3: Implement lifecycle filtering**

Allowed lifecycle values: `REGISTERED_INERT`, `ACTIVE`, `HISTORICAL`, `RETIRED`. Reject anything else.

- [ ] **Step 4: Correct Parallax facts**

Record topology PR merged as factual, but keep Parallax `REGISTERED_INERT` until first guarded append is durably recorded.

- [ ] **Step 5: Verify GREEN and commit**

Commit: `fix: separate registered and active writer lanes`.

---

### Task 4: Phase 2 node-level registry, leases, and exact routing

**Files:**
- Modify `src/radar/model.py`, `src/radar/registry.py`, `src/radar/routing.py`, `src/radar/runtime.py`.
- Modify `tests/radar/test_registry.py`, `tests/radar/test_routing.py`, `tests/radar/test_runtime_pipeline.py`.
- Add forward migration `supabase/migrations/20260906_radar_node_routing_hardening_v1.sql` with a unique timestamp assigned at commit time.
- Add `supabase/tests/radar_node_routing_hardening_v1.sql`.

**Interfaces:**

```python
@dataclass(frozen=True)
class Node:
    node_id: str
    identity_id: str
    status: NodeStatus
    last_heartbeat_ms: int | None = None
    lease_expires_ms: int | None = None

@dataclass(frozen=True)
class Subscription:
    node_id: str
    identity_id: str
    domain: str
    intent: str | None = None
    min_priority: int = 3
    enabled: bool = True
```

`IdentityRegistry.subscribe(node_id, *, domain, intent=None, min_priority=3)` returns a node-bound subscription. `Router.route()` returns exact node IDs in `RouteDecision.recipients`.

- [ ] **Step 1: RED tests**

Test that two nodes of one identity with different intents route only the matching live node; NULL/no lease is not routable; expired lease is not routable; paused/offline nodes are excluded.

- [ ] **Step 2: Verify RED**

Run: `python -m pytest -q tests/radar/test_registry.py tests/radar/test_routing.py tests/radar/test_runtime_pipeline.py`.

- [ ] **Step 3: Implement node-level in-process model**

Lease checks use explicit `now_ms` supplied by routing/runtime rather than wall-clock globals.

- [ ] **Step 4: Add forward SQL contract**

Create node-bound subscription columns/constraints and hardened stale-node semantics as forward changes; do not rewrite historical applied migrations.

- [ ] **Step 5: Verify GREEN and commit**

Commit: `feat: route Radar messages to exact live nodes`.

---

### Task 5: Phase 3 canonical dedupe key and Phase 4 accounting clarity

**Files:**
- Modify `src/radar/runtime.py`.
- Modify `tests/radar/test_runtime_pipeline.py` and heartbeat/telemetry tests.

- [ ] **Step 1: RED test canonical dedupe equivalence**

```python
def test_same_payload_hash_dedupes_across_route_context_inside_window():
    first = runtime.admit(message(audience=["one"]), now_ms=1000)
    second = runtime.admit(message(audience=["vera"]), now_ms=1200)
    assert first.state != "DROPPED_DUPLICATE"
    assert second.state == "DROPPED_DUPLICATE"
```

- [ ] **Step 2: Verify RED**

Expected: FAIL because `_dedupe_key()` currently re-hashes route context.

- [ ] **Step 3: Implement exact middleware key**

Replace `_dedupe_key()` with `return envelope.idempotency_key`; remove now-unused route-hash imports/helpers if no longer needed.

- [ ] **Step 4: Clarify routed accounting**

Keep heartbeat fields backwards compatible, but count `routed` only at the defined dispatch/handoff seam and add separate internal counters where matching/enqueueing needs visibility.

- [ ] **Step 5: Verify and commit**

Commit: `fix: restore canonical Radar dedupe semantics`.

---

### Task 6: Legacy Slack relay concurrency hardening

**Files:**
- Modify `src/chat_bus/slack_relay.py`.
- Modify `tests/chat_bus/test_slack_identity_relay.py`.

- [ ] **Step 1: RED concurrency tests**

Use two threads claiming the same operation and two threads racing `mark_delivered`; assert exactly one durable winner and every return value equals durable reread state.

- [ ] **Step 2: Verify RED**

Run: `python -m pytest -q tests/chat_bus/test_slack_identity_relay.py`.

- [ ] **Step 3: Implement locking/atomic claim**

Use explicit SQLite timeout, `check_same_thread=False`, an internal `RLock`, and transactional `INSERT ... ON CONFLICT`/conditional update semantics.

- [ ] **Step 4: Verify and commit**

Commit: `fix: harden legacy Slack relay concurrency`.

---

### Task 7: Durable reconciliation journal and trusted reconciler core

**Files:**
- Create `src/radar/reconciliation_journal.py`.
- Create `src/radar/trusted_reconciler.py`.
- Create forward migration `supabase/migrations/<new-version>_radar_projection_journal_v1.sql`.
- Create `supabase/tests/radar_projection_journal_v1.sql`.
- Add `tests/radar/test_reconciliation_journal.py` and `tests/radar/test_trusted_reconciler.py`.

**Interfaces:**

```python
class AncestryDisposition(str, Enum):
    NOOP = "NOOP"
    FORWARD = "FORWARD"
    STALE_EVENT = "STALE_EVENT"
    DIVERGED_HISTORY = "DIVERGED_HISTORY"

@dataclass(frozen=True)
class ReconcileTarget:
    identity: str
    branch: str
    projected_head: str | None
    observed_head: str
    commits: tuple[str, ...]
```

`TrustedReconciler.derive_target(identity: str | None = None) -> ReconcileTarget` reads canonical topology and Git itself; caller-provided heads/diffs are never accepted as authority.

- [ ] **Step 1: RED ancestry and stale-worker tests**

Prove `C==H`, forward ancestor, stale event, divergence, missing branch, and lost-lease finalization. A worker whose claim token no longer matches must receive `STALE_CLAIM` and must not advance the lane cursor.

- [ ] **Step 2: Verify RED**

Run new reconciliation tests.

- [ ] **Step 3: Implement pure Git derivation core**

The Python core may shell out to Git only against the trusted checkout/repository object database and treats writer branches as data; it never imports or executes branch files.

- [ ] **Step 4: Add journal SQL**

Tables: `radar.projection_lane_state`, `radar.projection_batches`, `radar.projection_batch_files`. Add service-role RPCs for claim, file-result recording, and fenced atomic finalize.

- [ ] **Step 5: Verify and commit trust anchor A**

Run Python + SQL artifact tests. Commit: `feat: add trusted Radar reconciliation journal`.

Record this commit SHA as immutable trust anchor `A` for Task 8.

---

### Task 8: Immutable trusted workflow and default-branch dispatcher

**Files:**
- Modify/create `.github/workflows/radar-trusted-projector.yml` at trust anchor A.
- Create `.github/workflows/radar-central-dispatcher.yml` in the following commit, pinning reusable workflow A exactly.
- Add/modify supply-chain workflow tests.

- [ ] **Step 1: RED workflow-source tests**

Assert reusable projector checks out `job.workflow_repository` at `job.workflow_sha`, all third-party actions are immutable SHAs, `persist-credentials: false`, and no target-branch script/action/artifact is executed.

- [ ] **Step 2: Verify RED**

Run workflow artifact tests.

- [ ] **Step 3: Commit immutable reusable workflow A**

If Task 7 code and reusable workflow cannot share one trust commit cleanly, make the reusable workflow the final file in the A commit and record exact SHA.

- [ ] **Step 4: Add dispatcher in successor commit**

Triggers:

```yaml
on:
  workflow_run:
    workflows: ["Writer Lane Guard"]
    types: [completed]
    branches: ["bus/**"]
  schedule:
    - cron: "*/5 * * * *"
```

Dispatcher passes only wake-up metadata; reusable reconciler independently resolves canonical ACTIVE lanes and heads.

- [ ] **Step 5: Verify and commit**

Commit: `feat: activate central Radar reconciliation source`.

---

### Task 9: Body-bound OIDC and replay ordering

**Files:**
- Modify `scripts/radar_emit_bus_projection.py` or replace its trusted-call path with reconciler-owned request emission.
- Modify `supabase/functions/github-bus-ingest/handler.ts`.
- Pin Edge imports and add deterministic Deno config/lock.
- Extend `tests/radar/test_emit_bus_projection.py` and Edge artifact tests.

- [ ] **Step 1: RED tests**

Assert exact-body SHA-256 audience `chat-communication-bus-supabase:<digest>`, matching digest header, fresh token/JTI per request, JTI consumption before semantic parse, and no JTI consumption when cryptographic body binding fails.

- [ ] **Step 2: Verify RED**

Run emitter/Edge tests.

- [ ] **Step 3: Implement exact-byte serialization**

Serialize once to bytes, hash those bytes, request OIDC token with bound audience, send same bytes.

- [ ] **Step 4: Rewrite Edge standard-claim assumptions**

Require exact repository + immutable `job_workflow_ref`/`job_workflow_sha` A + intended central caller class. Remove bus-push ref/head assumptions.

- [ ] **Step 5: Verify and commit**

Commit: `security: bind Radar projection OIDC to trusted request bytes`.

---

### Task 10: SQL CI, dependency pinning, and source custody

**Files:**
- Modify `.github/workflows/ci.yml`.
- Pin `pyproject.toml` build/test tooling through exact constraints.
- Pin Supabase Edge dependencies and add Deno lock/config.
- Replace `scripts/radar_source_hashes.py` with manifest-driven custody.
- Create `architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json`.
- Add custody tests.

- [ ] **Step 1: RED tests**

Assert no unbounded `pip install --upgrade pip`, exact pytest/build pins, immutable action refs, every `supabase/migrations/*_radar_*.sql`, every Radar SQL test, Edge source/config/lock, trusted workflows, topology contracts, and grammar fixtures are covered by custody.

- [ ] **Step 2: Verify RED**

Run supply-chain/custody tests.

- [ ] **Step 3: Add database CI job**

Use `supabase/setup-cli` pinned by immutable action SHA and an exact CLI version. Start local stack, execute `supabase db reset`, then run every Radar SQL assertion file.

- [ ] **Step 4: Verify and commit**

Commit: `build: make Radar recovery and dependency verification reproducible`.

---

### Task 11: Currentness, recovery, and incident documentation

**Files:**
- Modify `architecture/contracts/RADAR_CURRENT.json`.
- Modify `architecture/contracts/RADAR_SUPABASE_V1.md`.
- Modify `architecture/contracts/RADAR_SELF_REGISTRATION_V1.json`.
- Replace stale current seed semantics in `supabase/seed/radar_v1.sql` without rewriting dated historical snapshot seed.
- Modify `README.md`, `docs/operator/RECOVERY.md`, `docs/BRANCH_DISPOSITION.md`, Parallax onboarding/currentness docs, and add a successor Radar checkpoint.
- Update issue #16 narrative only after source implementation is complete; do not close it.

- [ ] **Step 1: RED currentness tests**

Assert current Radar mailbox is `bus/radar-v2`, Parallax factual topology state is not `TOPOLOGY_PR_PENDING`, migration list matches source chain, live/provider effects remain explicitly unapplied, and recovery never applies dated historical lane snapshots as current topology.

- [ ] **Step 2: Verify RED**

Run currentness/topology/self-registration tests.

- [ ] **Step 3: Update present-tense documents and seed**

Historical cutover/phase records remain historical and unchanged except for explicit labels where needed.

- [ ] **Step 4: Verify full source suite**

Run: `python -m compileall -q src && python -m pytest -q && python scripts/radar_source_hashes.py` plus the new local SQL CI-equivalent commands.

- [ ] **Step 5: Commit**

Commit: `docs: reconcile Radar currentness and recovery contracts`.

---

### Task 12: Final verification and review handoff

**Files:**
- No new behavior unless verification finds a defect.
- Update implementation PR body and issue #16 with source-only status.

- [ ] **Step 1: Exact-head verification**

Require Python 3.11/3.12 CI success, SQL reset/assertion job success, custody success, and no uncommitted/moving implementation head during review capture.

- [ ] **Step 2: Re-run hostile invariants**

Verify: no writer-branch code execution; no false cursor advance under lost lease/cancellation; no malformed Git message admitted that Edge rejects; no route to identity-only recipients; no replayable bound JTI after semantic parse failure; no migration-version collision.

- [ ] **Step 3: Update review PR**

State explicitly: `SOURCE IMPLEMENTED / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN`.

- [ ] **Step 4: Finish branch without merging**

Use the finishing-a-development-branch skill. Do not merge or deploy without separate Patrick authorization.
