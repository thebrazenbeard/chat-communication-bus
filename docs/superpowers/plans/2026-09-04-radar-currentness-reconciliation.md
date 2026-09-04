# Radar Currentness Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile the merged writer-lane v2 topology with the stale cutover receipt so Chat Bus current-route claims are source-correct, while preserving historical lanes as provenance and leaving Brigit on her explicit legacy lane until a separate activation.

**Architecture:** `RADAR_TOPOLOGY_V1.json` remains the authoritative current writer-lane registry. `RADAR_WRITER_LANE_V2_CUTOVER.json` becomes a post-merge receipt that records PR #12's observed merge, the 19 active successor routes, Brigit's current legacy exception, and the resolved duplicate-id history without silently activating `bus/brigit-v2`. Existing writer-lane code already resolves admissible refs from fresh topology, so the source repair is contract/test reconciliation rather than a new routing layer.

**Tech Stack:** JSON contracts, Python/pytest artifact tests, GitHub Actions CI.

**Spec:** `architecture/contracts/RADAR_TOPOLOGY_V1.json` + merged PR #12 evidence + `docs/protocol/COMMUNICATION_HUB_V1.md`

## Global Constraints

- Patrick remains sole merge authority.
- No provider deployment, Supabase migration, ruleset change, credential mutation, branch rewrite, or Brigit successor activation.
- Historical writer lanes remain durable provenance but are not current-route success when topology names another branch.
- External PR mirrors and estate counts must be refreshed from source GitHub state, not inferred from old Bus messages.

---

### Task 1: Encode the post-merge currentness expectation

**Files:**
- Modify: `tests/radar/test_writer_lane_v2_artifacts.py`

**Interfaces:**
- Consumes: `RADAR_TOPOLOGY_V1.json`, `RADAR_WRITER_LANE_V2_CUTOVER.json`
- Produces: regression expectations for merged cutover state and Brigit's explicit exception

- [ ] **Step 1: Write the failing test**

Change the artifact tests to require:

```python
assert cutover["status"] == "TOPOLOGY_SWITCH_EFFECTIVE_WITH_BRIGIT_LEGACY_EXCEPTION"
assert cutover["topology_switched"] is True
assert cutover["topology_switch_merge_sha"] == "0dc9f821be363c2862309c166ec2eb43b4879b37"
assert cutover["current_writer_lanes"] == {
    identity: record["branch"]
    for identity, record in topology["required_writer_lanes"].items()
}
assert cutover["current_writer_lanes"]["brigit"] == "bus/bridget-v1"
```

Also require the Brigit exception to record correction message `brigit-0025`, acknowledgement `brigit-0026`, and `successor_activation_performed is False`.

- [ ] **Step 2: Run CI to verify RED**

Push only the test change. Expected result: pytest fails because the current receipt still says `PARTIAL_TOPOLOGY_SWITCH_PROPOSED` / `topology_switched: false` and lacks post-merge/current-lane fields.

### Task 2: Reconcile the canonical contracts

**Files:**
- Modify: `architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json`
- Modify: `architecture/contracts/RADAR_TOPOLOGY_V1.json`

**Interfaces:**
- Consumes: merged PR #12 SHA/time, current topology, Brigit append-only correction evidence
- Produces: one unambiguous current-route source surface

- [ ] **Step 1: Update the cutover receipt**

Set the receipt to post-merge effective state, record merge SHA `0dc9f821be363c2862309c166ec2eb43b4879b37` and merge time `2026-09-04T11:37:28Z`, add `current_writer_lanes` exactly matching topology, preserve predecessor and verified-successor snapshots, replace the stale active block with a historical block plus explicit Brigit legacy exception, and record no provider/ruleset effect.

- [ ] **Step 2: Update topology notes**

State explicitly that `required_writer_lanes` is current write-routing authority; historical lane existence is provenance only. Replace the stale note that Brigit is waiting for duplicate-id correction with the current fact that the correction is complete but `bus/brigit-v2` has not been separately activated.

- [ ] **Step 3: Run CI to verify GREEN**

Expected: full pytest passes on Python 3.11 and 3.12 and source-hash verification succeeds.

### Task 3: Publish the bounded source repair

**Files:**
- No additional source files required.

**Interfaces:**
- Consumes: verified branch head
- Produces: one reviewable Radar PR; no protected effect

- [ ] **Step 1: Compare branch to `main`**

Confirm only the plan, topology contract, cutover receipt, and regression test changed.

- [ ] **Step 2: Open a draft PR to `main`**

Describe the root cause, RED/GREEN evidence, source-only scope, Brigit non-activation, and protected effects not performed.

- [ ] **Step 3: Do not merge**

Patrick retains merge authority.

### Task 4: Refresh coordination currentness outside the source PR

**Files/surfaces:**
- `hub/pr-mirrors-v1` communication branch
- `chat-communication-bus#10`

**Interfaces:**
- Consumes: live GitHub source PR/issue state
- Produces: current Bus coordination snapshot without redefining canonical protocol

- [ ] **Step 1: Refresh PR mirror currentness**

Preserve historical mirror records, append current-status successors for `vera-os#1` (merged) and `vera-control-plane#6` (open Draft), and refresh the mirror index from the live open-PR query.

- [ ] **Step 2: Refresh estate issue #10**

Add a source-backed currentness comment recording `19` open issues and `7` open PRs with the exact GitHub Search queries and `incomplete_results=false`.

- [ ] **Step 3: Verify readback**

Re-read both communication surfaces and make no broader currentness claim than the timestamped source snapshot supports.
