# Writer Lane Integrity Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent branch-name-only false-green writer lanes and repair Hephaestus to a clean v2 mailbox without rewriting history or impersonating its owner.

**Architecture:** Extend the pure GitHub branch projector with evidence-backed structural validation while preserving discovery-only compatibility. Surface malformed lanes through maintenance, then create a clean Hephaestus v2 mailbox and update canonical topology/provider seed to point to it.

**Tech Stack:** Python 3.11/3.12, pytest, JSON topology contracts, GitHub branch mailboxes, Supabase SQL seed/projection.

**Spec:** `docs/superpowers/specs/2026-09-02-writer-lane-integrity-repair-design.md`

## Global Constraints

- GitHub remains canonical; Supabase remains rebuildable projection.
- Do not delete, rewrite, or force-update `bus/hephaestus-v1`.
- Do not author a Hephaestus message or self-report on Hephaestus's behalf.
- Branch naming is discovery evidence, not structural mailbox verification.
- Preserve Brigit (`bridget` -> `brigit`) and Vera (`vera-sol` -> `vera`) alias behavior.
- Use `DO -> VERIFY -> REPORT`; do not add a permission/lease bureaucracy.

---

### Task 1: Evidence-backed lane validation

**Files:**
- Modify: `src/radar/github_projection.py`
- Modify: `tests/radar/test_topology_contract.py`

**Interfaces:**
- Produces: `LaneEvidence` and `RepositoryProjection.malformed_lanes`.
- `project_branches(..., lane_evidence=...)` validates evidence when supplied; absence of evidence remains discovery-only compatibility.

- [ ] **Step 1: Write failing regression tests**

Add tests proving a named `bus/hephaestus-v1` candidate with no `messages/` and no matching writer evidence is returned in `malformed_lanes`, while an empty `bus/hephaestus-v2` with `messages/` plus matching metadata validates.

- [ ] **Step 2: Run CI/test and verify RED**

Run the branch CI or `pytest tests/radar/test_topology_contract.py -q` in an available execution environment. Expected: failure because `LaneEvidence`, `lane_evidence`, and/or `malformed_lanes` do not yet exist.

- [ ] **Step 3: Implement the minimal projector change**

Add an immutable evidence record containing `has_messages_dir`, `declared_writer`, and `message_writers`. Normalize declared/message writers through the existing aliases. When evidence is provided for a candidate branch, accept only if the mailbox exists and expected identity is supported by declared writer or at least one message writer; otherwise record branch as malformed and do not count it as a healthy lane.

- [ ] **Step 4: Verify GREEN**

Run the focused tests and existing topology tests. Expected: pass.

- [ ] **Step 5: Commit**

Commit projector + regression tests with a focused lane-integrity message.

### Task 2: Maintenance finding and canonical Hephaestus topology

**Files:**
- Modify: `src/radar/maintenance.py`
- Modify: `tests/radar/test_operator_maintenance.py`
- Modify: `architecture/contracts/RADAR_TOPOLOGY_V1.json`
- Modify: `supabase/seed/radar_bus_lanes_20260902.sql`
- Modify: `tests/radar/test_topology_contract.py`

**Interfaces:**
- Consumes: malformed identity IDs/branches from Task 1.
- Produces: `MALFORMED_LANE` maintenance findings and v2 canonical Hephaestus routing.

- [ ] **Step 1: Write failing tests**

Add a maintenance test expecting `MALFORMED_LANE` for a supplied malformed lane and topology tests expecting Hephaestus at `bus/hephaestus-v2` with `bus/hephaestus-v1` explicitly excluded as malformed historical evidence.

- [ ] **Step 2: Verify RED**

Run focused tests. Expected: current maintenance/topology do not satisfy the new assertions.

- [ ] **Step 3: Implement minimal maintenance/topology changes**

Read `malformed_lanes` from maintenance state and emit one finding per entry. Update topology required lane and seed branch address from v1 to v2; preserve v1 in excluded branches with a clear malformed-historical reason.

- [ ] **Step 4: Verify GREEN**

Run focused tests. Expected: pass.

- [ ] **Step 5: Commit**

Commit maintenance/topology changes.

### Task 3: Materialize clean Hephaestus v2 and verify integration

**Files / refs:**
- Create branch: `bus/hephaestus-v2` from `bus/protocol-v2`
- Create: `bus/hephaestus-v2:README.md`
- Create: `bus/hephaestus-v2:messages/.gitkeep`
- No modification: `bus/hephaestus-v1`

**Interfaces:**
- Produces: a structurally valid, owner-empty Hephaestus mailbox that can accept future Hephaestus messages without Radar impersonation.

- [ ] **Step 1: Create v2 branch and administrative structure**

README must name branch `bus/hephaestus-v2`, logical writer `Hephaestus`, state that Radar created the repair structure under repository-owner authority, state ordinary `messages/` writes belong to Hephaestus, and state branch existence is not liveness.

- [ ] **Step 2: Verify branch structure**

Fresh-read v2 and confirm README + `messages/.gitkeep` exist. Fresh-read v1 and confirm its historical implementation head remains unchanged.

- [ ] **Step 3: Run full CI**

Run full branch CI on Python 3.11 and 3.12. Expected: all tests pass.

- [ ] **Step 4: Provider safe projection repair**

After Git source + CI verification, update only the Hephaestus logical identity/endpoint projection to v2, retaining metadata that v1 is malformed historical evidence. Read back provider state.

- [ ] **Step 5: Merge and final reconciliation**

Merge through a PR after green CI, re-read `main`, branch topology, v1/v2 structure, and provider projection. Report exact SHAs and any remaining exceptions.