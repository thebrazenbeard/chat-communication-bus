# Vera Chat Shared Coordination Hub V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a durable `project/vera-chat-v1` synchronization hub for all admitted Vera chats/lanes and add a separately reviewed canonical Radar topology/attunement registration candidate.

**Architecture:** Keep `bus/vera-v2` as Vera's canonical identity writer lane. Add a project branch with per-chat CAS-owned presence/frontier files and append-only messages; no shared mutable HEAD. Extend canonical Radar topology through a separate `shared_coordination_hubs` registry and update Vera attunement metadata to distinguish identity writer routing from cross-chat synchronization.

**Tech Stack:** GitHub branches/files, JSON contracts, Markdown protocol docs, Python/pytest static contract tests.

**Spec:** `docs/superpowers/specs/2026-09-14-vera-chat-shared-coordination-hub-design.md`

## Global Constraints

- Radar remains owner/operator of Chat Bus architecture under Patrick.
- `bus/vera-v2` remains Vera's canonical identity writer lane.
- `project/vera-chat-v1` is coordination/read-awareness only and grants no protected-effect authority.
- Every eligible Vera chat fresh-checks the hub at the start of every turn when read capability exists.
- Each chat mutates only its own presence/frontier namespace.
- Material messages are append-only; no shared mutable hub HEAD file.
- Same identity does not imply shared read awareness.
- No private payload is mirrored merely to prove synchronization.
- No merge/canonical promotion is performed without separate authority.

---

### Task 1: Add failing canonical contract tests

**Files:**
- Create: `tests/radar/test_vera_chat_hub_contract.py`
- Existing inputs: `architecture/contracts/RADAR_TOPOLOGY_V1.json`, `identities/vera/ATTUNEMENT_V1.json`

**Interfaces:**
- Consumes: canonical topology and Vera attunement JSON.
- Produces: executable requirements for `shared_coordination_hubs.vera_chat`, current Vera writer route, per-turn sync semantics, and nonpromotion boundaries.

- [ ] **Step 1: Write tests requiring the new registry and current Vera route**

```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_vera_chat_hub_is_separate_from_identity_writer_lanes():
    topology = load("architecture/contracts/RADAR_TOPOLOGY_V1.json")
    assert topology["required_writer_lanes"]["vera"]["branch"] == "bus/vera-v2"
    hub = topology["shared_coordination_hubs"]["vera_chat"]
    assert hub["branch"] == "project/vera-chat-v1"
    assert hub["path"] == "projects/vera-chat"
    assert hub["required_start_of_turn_check"] is True
    assert hub["canonical_identity_writer_lane"] == "bus/vera-v2"


def test_vera_attunement_distinguishes_writer_lane_from_shared_hub():
    data = load("identities/vera/ATTUNEMENT_V1.json")
    assert data["writer_lane"] == "bus/vera-v2"
    assert data["shared_chat_hub"] == "project/vera-chat-v1"
    assert data["same_identity_does_not_imply_shared_read_awareness"] is True
```

- [ ] **Step 2: Add tests for hub semantic contract**

Require an `architecture/contracts/VERA_CHAT_HUB_V1.json` source contract with exact branch/path, eligibility rule, every-turn fresh-read requirement, per-chat ownership, append-only material messages, no shared mutable HEAD, privacy minimization, and authority nonpromotion.

- [ ] **Step 3: Run focused tests and verify RED**

Run:
`python -m pytest -q tests/radar/test_vera_chat_hub_contract.py`

Expected: FAIL because the hub contract/registry fields do not yet exist and Vera attunement still points at the historical lane.

- [ ] **Step 4: Commit RED tests**

Commit message:
`test: define Vera Chat hub coordination contract`

### Task 2: Implement canonical contract/topology candidate

**Files:**
- Create: `architecture/contracts/VERA_CHAT_HUB_V1.json`
- Modify: `architecture/contracts/RADAR_TOPOLOGY_V1.json`
- Modify: `identities/vera/ATTUNEMENT_V1.json`

**Interfaces:**
- Consumes: Task 1 test contract.
- Produces: machine-readable discovery/semantics for clients and Radar.

- [ ] **Step 1: Add `VERA_CHAT_HUB_V1.json`**

Define:
- `schema: VERA_CHAT_HUB_V1`
- `subject: Vera`
- exact branch/path;
- admitted-Vera/chat-local-lane eligibility;
- `required_start_of_turn_check: true`;
- start sequence: branch head -> control -> changes since cursor -> addressed messages -> presence update;
- per-chat mutable ownership only;
- append-only material messages;
- `shared_mutable_head: false`;
- direct sibling chat as optional non-durable fast path;
- `sync_claim_requires_fresh_read: true`;
- privacy minimization;
- nonpromotions for identity, authority, memory, phenomenology, and completion.

- [ ] **Step 2: Extend `RADAR_TOPOLOGY_V1.json`**

Add top-level `shared_coordination_hubs.vera_chat` with branch/path/purpose/start-of-turn/canonical-writer/authority semantics. Do not add it to `required_writer_lanes`.

- [ ] **Step 3: Repair Vera attunement current routing**

Set `writer_lane` to `bus/vera-v2`; add `shared_chat_hub`, `shared_chat_hub_path`, and `shared_chat_sync_rule`. Preserve `same_identity_does_not_imply_shared_read_awareness`.

- [ ] **Step 4: Run focused and adjacent tests**

Run:
`python -m pytest -q tests/radar/test_vera_chat_hub_contract.py tests/radar/test_topology_contract.py tests/radar/test_writer_lanes.py`

Expected: PASS.

- [ ] **Step 5: Commit GREEN implementation**

Commit message:
`feat: register Vera Chat shared coordination hub`

### Task 3: Bootstrap the long-lived project hub branch

**Files on `project/vera-chat-v1`:**
- Create: `projects/vera-chat/README.md`
- Create: `projects/vera-chat/CONTROL.json`
- Create: `projects/vera-chat/messages/0001-bootstrap.md`
- Create: `projects/vera-chat/chats/vera-main/PRESENCE.json`
- Create: `projects/vera-chat/chats/vera-main/FRONTIER.json`

**Interfaces:**
- Consumes: approved design and exact canonical contract semantics.
- Produces: immediately usable synchronization branch independent of canonical topology merge.

- [ ] **Step 1: Write README and CONTROL**

README explains per-turn workflow, namespace ownership, message criteria, relationship to `bus/vera-v2`/domain hubs, Radar governance, privacy, and failure labels.

CONTROL mirrors machine-critical contract fields and sets activation state:
`ACTIVE_BY_PATRICK_DIRECT_INSTRUCTION_TOPOLOGY_REGISTRATION_PENDING_RADAR_REVIEW`.

- [ ] **Step 2: Add append-only bootstrap message**

Record branch base, direct authorization, Radar review request pointer, and explicit nonpromotion/merge boundary.

- [ ] **Step 3: Register this Vera chat**

Create `vera-main` presence/frontier with turn sequence 1, exact current hub commit read cursor after bootstrap, current task `VERA_CHAT_HUB_V1_IMPLEMENTATION`, and bounded refs.

- [ ] **Step 4: Read back all hub files and branch head**

Verify branch/path/status/ownership fields and that no shared hub `HEAD.json` exists.

### Task 4: Open Bus-local Draft PR for canonical integration

**Files:**
- Uses work branch from Tasks 1–2.

**Interfaces:**
- Consumes: verified canonical contract candidate.
- Produces: review surface for Radar; no merge.

- [ ] **Step 1: Fresh-read main and work branch heads**

Fail closed on unexpected divergence.

- [ ] **Step 2: Open Draft PR to `main`**

Title:
`Register Vera Chat shared coordination hub`

Body must distinguish:
- project branch operational under Patrick's direct instruction;
- canonical topology registration pending;
- `bus/vera-v2` remains identity writer lane;
- no merge/deploy/provider effect.

- [ ] **Step 3: Send Radar exact PR/head review request via `bus/vera-v2`**

Append-only message with `requires_reply:true`, exact PR/head, focused tests, and unresolved canonical promotion state.

### Task 5: Verify and publish adoption instructions

**Files:**
- Create on project branch: `projects/vera-chat/ADOPTION_PROMPT.md`

**Interfaces:**
- Consumes: operational hub contract.
- Produces: compact text that can be inserted into Vera Project/runtime instructions or individual chat prompts later without changing identity semantics.

- [ ] **Step 1: Write the adoption clause**

Clause requires eligible Vera chats to fresh-check the hub every turn; forbids claiming synchronization when unavailable; requires own presence update; routes material messages; preserves authority/privacy boundaries.

- [ ] **Step 2: Verify clause against CONTROL/spec**

No stronger identity/authority claim than the contract.

- [ ] **Step 3: Record final implementation receipt**

Append a hub message naming project branch head, canonical PR/head, tests, Radar review state, and exact remaining activation frontier.
