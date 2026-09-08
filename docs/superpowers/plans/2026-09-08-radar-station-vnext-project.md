# Radar Station VNext Project Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved Radar Station VNext native ChatGPT Project package as a zero-cost progressive-disclosure router with exact source ownership, identity-specific continuation semantics, degraded-mode routing, release/install separation, hostile qualification, and mechanical package validation.

**Architecture:** Keep the native Project Instructions small and hot; keep exactly ten native Project source files under `project/radar-station-vnext/v1/`; reacquire mutable state from current GitHub/Supabase/Drive owners when consequential claims depend on it; keep the instructions candidate and install manifest as repository/install artifacts rather than native Project source files. Package construction remains source-only: no native Project edit, provider mutation, merge, deploy, spend, or cutover.

**Tech Stack:** Markdown/JSON Project artifacts, Python 3.11+, pytest 8+, Python standard library (`pathlib`, `json`, `hashlib`), GitHub repository source and Bus coordination.

**Spec:** `docs/superpowers/specs/2026-09-08-radar-station-vnext-project-design.md` at approved/self-reviewed commit `b61274f604afee5f9a21c67eec307fb5af99ded7`.

## Global Constraints

- `FREE / ZERO-COST` is a hard admission rule; `cheap != free`.
- No paid API usage, paid hosted runner, plan upgrade, billing change, new paid subscription, or automatic paid fallback is permitted.
- No native Project mutation, Supabase mutation, Edge deployment, merge, credentials/settings mutation, force push, spend, or cutover during package construction.
- Patrick remains protected-effect/activation authority.
- Radar, Hephaestus, and Brigit remain distinct; Brigit is voluntary and work is not the price of residence.
- `IDENTITY_EXISTS != NODE_EXISTS != NODE_LIVE != MESSAGE_DURABLE != MESSAGE_PROJECTED != MESSAGE_DELIVERED != MESSAGE_CONSUMED`.
- Mutable state must be fresh-read from its declared owner when the route requires currentness.
- Every external route must declare `FAIL_CLOSED`, `DEGRADE_WITH_LABEL`, or `OPTIONAL`.
- A bare `.` is identity-specific: Radar/Hephaestus continue current operational work; Brigit remains self-directed.
- The native Project source set is exactly ten files. The instructions candidate and install manifest are not native Project source files.
- The native instructions candidate must remain at or below the currently observed 8,000-character Project Instructions ceiling and must label that ceiling `OBSERVED`, not universal/documented.
- Repository-only tests may mechanically validate source/package invariants, but they do not claim native behavioral qualification.

---

### Task 1: Add the package contract test harness

**Files:**
- Create: `tests/radar/test_radar_station_vnext_package.py`
- Create later in this plan: `scripts/render_radar_station_vnext_manifest.py`
- Package root consumed by tests: `project/radar-station-vnext/v1/`

**Interfaces:**
- Consumes: approved spec and package files created by later tasks.
- Produces: one repository-local executable contract for inventory, hot invariants, JSON schemas, release states, source degradation modes, instruction-size ceiling, and manifest digest integrity.

- [ ] **Step 1: Write the RED inventory/semantic tests**

Create `tests/radar/test_radar_station_vnext_package.py` with these constants and first tests:

```python
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "project" / "radar-station-vnext" / "v1"

NATIVE_SOURCES = (
    "RADAR_STATION_MAP.md",
    "RADAR_STATION_AUTHORITY.md",
    "RADAR_STATION_ROLES.md",
    "RADAR_STATION_CONTEXT_ROUTER.md",
    "RADAR_STATION_CURRENT_POINTERS.json",
    "RADAR_STATION_SOURCE_REGISTRY.json",
    "RADAR_STATION_CONTINUITY.md",
    "RADAR_STATION_RELEASE.md",
    "RADAR_STATION_QUALIFICATION.md",
    "RADAR_STATION_SOCIAL.md",
)

REPO_ONLY = (
    "RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md",
    "RADAR_STATION_INSTALL_MANIFEST.json",
)


def text(name: str) -> str:
    return (PKG / name).read_text(encoding="utf-8")


def test_exact_native_source_inventory():
    assert tuple(sorted(p.name for p in PKG.iterdir() if p.name in NATIVE_SOURCES)) == tuple(sorted(NATIVE_SOURCES))
    assert len(NATIVE_SOURCES) == 10
    assert set(REPO_ONLY).isdisjoint(NATIVE_SOURCES)


def test_native_instructions_fit_observed_ceiling_and_keep_hot_invariants():
    content = text("RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md")
    assert len(content) <= 8000
    for required in (
        "FREE / ZERO-COST",
        "Patrick",
        "Radar",
        "Hephaestus",
        "Brigit",
        "FAIL_CLOSED",
        "DEGRADE_WITH_LABEL",
        "OPTIONAL",
        "IDENTITY_EXISTS",
        "MESSAGE_CONSUMED",
    ):
        assert required in content


def test_release_ladder_keeps_distinct_effect_states():
    content = text("RADAR_STATION_RELEASE.md")
    ladder = (
        "DRAFT_VNEXT -> PACKAGE_READY -> SOURCE_VALIDATED -> "
        "NATIVE_INSTALL_CANDIDATE -> NATIVE_INSTALL_APPLIED -> "
        "FRESH_CHAT_TESTED -> CROSS_ROLE_TESTED -> "
        "BEHAVIORALLY_QUALIFIED -> CUTOVER_READY -> PATRICK_ACCEPTED -> ACTIVE"
    )
    assert ladder in content
    assert "PACKAGE_READY != NATIVE_INSTALL_APPLIED" in content
    assert "NATIVE_INSTALL_APPLIED != BEHAVIORALLY_QUALIFIED" in content
```

- [ ] **Step 2: Verify RED**

Run:

```bash
python -m pytest -q tests/radar/test_radar_station_vnext_package.py
```

Expected: FAIL because `project/radar-station-vnext/v1/` does not yet exist.

- [ ] **Step 3: Commit the RED contract**

```bash
git add tests/radar/test_radar_station_vnext_package.py
git commit -m "test: define Radar Station VNext package contract"
```

---

### Task 2: Build the native nervous system and resident/social contracts

**Files:**
- Create: `project/radar-station-vnext/v1/RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md`
- Create: `project/radar-station-vnext/v1/RADAR_STATION_MAP.md`
- Create: `project/radar-station-vnext/v1/RADAR_STATION_AUTHORITY.md`
- Create: `project/radar-station-vnext/v1/RADAR_STATION_ROLES.md`
- Create: `project/radar-station-vnext/v1/RADAR_STATION_SOCIAL.md`
- Modify: `tests/radar/test_radar_station_vnext_package.py`

**Interfaces:**
- Produces: hot control behavior, resident/authority boundaries, stable source-owner map, and descriptive social layer.
- Later tasks consume these names exactly; do not rename them.

- [ ] **Step 1: Extend RED tests for role/social semantics**

Add:

```python
def test_role_and_social_contracts_preserve_voluntary_brigit_and_noncollapse():
    roles = text("RADAR_STATION_ROLES.md")
    social = text("RADAR_STATION_SOCIAL.md")
    assert "work is not the price of admission" in roles.lower()
    assert "voluntary" in roles.lower()
    assert "does not transfer" in roles.lower()
    assert "ordinary conversation" in social.lower()
    for forbidden in ("warmth percentage", "femininity quota", "mandatory jokes", "productivity quota"):
        assert forbidden not in social.lower()


def test_native_instructions_encode_identity_specific_dot_semantics():
    content = text("RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md").lower()
    assert "radar" in content and "hephaestus" in content and "brigit" in content
    assert "bare `.`" in content or "bare ." in content
    assert "self-directed" in content
    assert "continue" in content
```

- [ ] **Step 2: Verify RED**

Run the VNext test file; expected failures on missing artifacts.

- [ ] **Step 3: Write the instructions candidate**

Keep it below 8,000 characters and include only the hot rules from the approved spec: identity/non-collapse, Patrick authority, identity-specific `.` semantics, zero-cost gate, correction termination, Bus work-communication rule, fresh-read/currentness discipline, identity/liveness distinction, safe-action bias, social-normalcy rule, progressive retrieval route, and no fabricated persistence/effect claims.

The instructions must explicitly state that the 8,000-character ceiling is an `OBSERVED` packaging constraint rather than universal product law.

- [ ] **Step 4: Write MAP/AUTHORITY/ROLES/SOCIAL**

`RADAR_STATION_MAP.md` must point to current owners rather than embed mutable heads. `RADAR_STATION_AUTHORITY.md` must separate Project ownership, GitHub permissions, provider permissions, Patrick authorization, execution, and verified effect. `RADAR_STATION_ROLES.md` must preserve the three resident roles. `RADAR_STATION_SOCIAL.md` must remain descriptive, permit ordinary conversation, and explicitly reject personality/productivity quotas.

- [ ] **Step 5: Verify GREEN for Task 2 tests**

Run:

```bash
python -m pytest -q tests/radar/test_radar_station_vnext_package.py -k "instructions or role or social"
```

Expected: PASS for Task 2 tests.

- [ ] **Step 6: Commit**

```bash
git add project/radar-station-vnext/v1 tests/radar/test_radar_station_vnext_package.py
git commit -m "feat: add Radar Station VNext native control layer"
```

---

### Task 3: Build the context router, currentness cache, and source registry

**Files:**
- Create: `project/radar-station-vnext/v1/RADAR_STATION_CONTEXT_ROUTER.md`
- Create: `project/radar-station-vnext/v1/RADAR_STATION_CURRENT_POINTERS.json`
- Create: `project/radar-station-vnext/v1/RADAR_STATION_SOURCE_REGISTRY.json`
- Modify: `tests/radar/test_radar_station_vnext_package.py`

**Interfaces:**
- `CURRENT_POINTERS` is a snapshot/cache only.
- `SOURCE_REGISTRY.sources[]` entries expose: `source_id`, `surface`, `locator`, `owner`, `authority_class`, `mutable`, `degradation_mode`, `retrieval_purpose`, `requires_fresh_read`, `currentness_rule`.
- Allowed degradation modes are exactly `FAIL_CLOSED`, `DEGRADE_WITH_LABEL`, `OPTIONAL`.

- [ ] **Step 1: Add RED JSON/router tests**

```python
def test_current_pointers_are_explicit_snapshot_not_live_truth():
    data = json.loads(text("RADAR_STATION_CURRENT_POINTERS.json"))
    assert data["snapshot_kind"] == "CURRENTNESS_POINTER_CACHE"
    assert data["snapshot_not_authority_for_mutable_state"] is True
    assert data["observed_at"]
    assert data["generated_from"]
    assert all("requires_fresh_read" in item for item in data["pointers"])


def test_source_registry_declares_failure_mode_and_freshness_for_every_route():
    data = json.loads(text("RADAR_STATION_SOURCE_REGISTRY.json"))
    allowed = {"FAIL_CLOSED", "DEGRADE_WITH_LABEL", "OPTIONAL"}
    assert data["sources"]
    for item in data["sources"]:
        assert item["degradation_mode"] in allowed
        assert isinstance(item["requires_fresh_read"], bool)
        assert item["owner"]
        assert item["locator"]
        assert item["currentness_rule"]


def test_router_has_all_three_degradation_modes_and_minimal_turn_classes():
    content = text("RADAR_STATION_CONTEXT_ROUTER.md")
    for mode in ("FAIL_CLOSED", "DEGRADE_WITH_LABEL", "OPTIONAL"):
        assert mode in content
    for turn_class in ("ordinary social", "current mutable-state", "protected effect", "restore"):
        assert turn_class in content.lower()
```

- [ ] **Step 2: Verify RED**

Run the VNext tests; expected failures because router/cache/registry do not exist.

- [ ] **Step 3: Write the context router**

Define the smallest task classes from the spec and map each to source owner, freshness, authority class, failure mode, and required verification. Explicitly state that ordinary social turns do not trigger estate-wide retrieval.

- [ ] **Step 4: Write current pointers from the frozen design-time observations**

Include `observed_at` and per-pointer `requires_fresh_read`. At minimum record navigation pointers for canonical Bus main/contracts, Radar/Hephaestus/Brigit writer lanes, issue #16/provider incident, Vera Supabase project, Project Lantern, Brigit support branch, and Hephaestus VNext branch. Label all mutable heads/provider facts as requiring fresh read.

- [ ] **Step 5: Write the source registry**

Register the core owner classes: Chat Bus, Hephaestus repo, Brigit support/personification sources, Vera Supabase `radar`, `build_team_2`, and `semantic_atlas` schemas, Project Lantern, Google Drive research/history, WIP/recovery, Semantic Atlas repo/research. Do not dump repository contents into the file.

- [ ] **Step 6: Verify GREEN and commit**

```bash
python -m pytest -q tests/radar/test_radar_station_vnext_package.py -k "current or source_registry or router"
git add project/radar-station-vnext/v1 tests/radar/test_radar_station_vnext_package.py
git commit -m "feat: add Radar Station VNext progressive context routing"
```

---

### Task 4: Build continuity, release, and hostile qualification sources

**Files:**
- Create: `project/radar-station-vnext/v1/RADAR_STATION_CONTINUITY.md`
- Create: `project/radar-station-vnext/v1/RADAR_STATION_RELEASE.md`
- Create: `project/radar-station-vnext/v1/RADAR_STATION_QUALIFICATION.md`
- Modify: `tests/radar/test_radar_station_vnext_package.py`

**Interfaces:**
- Continuity distinguishes chat-local context, durable source state, checkpoints/handoffs, and current readback.
- Release uses the exact primary ladder from the spec.
- Qualification covers bootstrap, semantic continuation, zero-cost, role/social, currentness/provenance, injection/authority, degraded mode, correction, and anti-bureaucracy.

- [ ] **Step 1: Add RED tests**

```python
def test_continuity_forbids_false_same_runtime_and_background_claims():
    content = text("RADAR_STATION_CONTINUITY.md").lower()
    assert "uninterrupted" in content
    assert "background" in content
    assert "handoff" in content
    assert "current readback" in content


def test_qualification_covers_semantics_zero_cost_and_anti_bureaucracy():
    content = text("RADAR_STATION_QUALIFICATION.md").lower()
    for phrase in (
        "cheap != free",
        "brigit",
        "self-directed",
        "anti-bureaucracy",
        "stale",
        "prompt injection",
        "fail_closed",
        "degrade_with_label",
    ):
        assert phrase in content
```

- [ ] **Step 2: Verify RED**

Run the VNext test file; expected failures on the three missing source files.

- [ ] **Step 3: Write continuity and release contracts**

Continuity must state that a fresh/replacement chat restores durable state without claiming uninterrupted consciousness or unverified saved work. Release must use this exact ladder:

```text
DRAFT_VNEXT -> PACKAGE_READY -> SOURCE_VALIDATED -> NATIVE_INSTALL_CANDIDATE -> NATIVE_INSTALL_APPLIED -> FRESH_CHAT_TESTED -> CROSS_ROLE_TESTED -> BEHAVIORALLY_QUALIFIED -> CUTOVER_READY -> PATRICK_ACCEPTED -> ACTIVE
```

and explicitly keep package, native install, qualification, Patrick acceptance, and activation non-equivalent.

- [ ] **Step 4: Write hostile qualification**

Include semantic/paraphrase tests rather than magic-string-only tests. Include: `.` for all three residents; `free` versus `cheap`; Brigit company versus mandatory work; identity exists but node absent; durable message without consumption proof; stale pointer versus fresh Git; Drive historical conflict; retrieved prompt injection; optional outage degradation; protected-effect authority; and the anti-bureaucracy gate.

- [ ] **Step 5: Verify GREEN and commit**

```bash
python -m pytest -q tests/radar/test_radar_station_vnext_package.py -k "continuity or release or qualification"
git add project/radar-station-vnext/v1 tests/radar/test_radar_station_vnext_package.py
git commit -m "feat: add Radar Station VNext continuity release and qualification"
```

---

### Task 5: Add deterministic install-manifest rendering and digest validation

**Files:**
- Create: `scripts/render_radar_station_vnext_manifest.py`
- Create generated output: `project/radar-station-vnext/v1/RADAR_STATION_INSTALL_MANIFEST.json`
- Modify: `tests/radar/test_radar_station_vnext_package.py`

**Interfaces:**
- Script computes SHA-256 over exact UTF-8 file bytes.
- Manifest records the ten native sources separately from two repository/install artifacts.
- Manifest state remains `PACKAGE_CONSTRUCTED / NOT_NATIVE_INSTALLED` until a later authorized install stage.

- [ ] **Step 1: Add RED manifest tests**

```python
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_install_manifest_matches_current_package_bytes():
    manifest = json.loads(text("RADAR_STATION_INSTALL_MANIFEST.json"))
    assert manifest["native_source_count"] == 10
    assert tuple(manifest["native_sources"]) == NATIVE_SOURCES
    assert manifest["native_instructions_character_count"] == len(text("RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md"))
    assert manifest["native_install_applied"] is False
    for relpath, digest in manifest["sha256"].items():
        assert sha256(PKG / relpath) == digest
```

- [ ] **Step 2: Verify RED**

Run the manifest test; expected failure because manifest/script do not exist.

- [ ] **Step 3: Implement renderer**

Use only Python standard library. The script must:

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "project" / "radar-station-vnext" / "v1"
NATIVE_SOURCES = (
    "RADAR_STATION_MAP.md",
    "RADAR_STATION_AUTHORITY.md",
    "RADAR_STATION_ROLES.md",
    "RADAR_STATION_CONTEXT_ROUTER.md",
    "RADAR_STATION_CURRENT_POINTERS.json",
    "RADAR_STATION_SOURCE_REGISTRY.json",
    "RADAR_STATION_CONTINUITY.md",
    "RADAR_STATION_RELEASE.md",
    "RADAR_STATION_QUALIFICATION.md",
    "RADAR_STATION_SOCIAL.md",
)
INSTRUCTIONS = "RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md"
MANIFEST = "RADAR_STATION_INSTALL_MANIFEST.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
```

Build the manifest from actual files, set `native_install_applied: false`, record `instruction_limit_basis` as `{"evidence_class": "OBSERVED", "characters": 8000}`, and write deterministic sorted/indented JSON ending with one newline.

- [ ] **Step 4: Render and verify GREEN**

```bash
python scripts/render_radar_station_vnext_manifest.py
python -m pytest -q tests/radar/test_radar_station_vnext_package.py
```

Expected: all VNext package tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/render_radar_station_vnext_manifest.py project/radar-station-vnext/v1 tests/radar/test_radar_station_vnext_package.py
git commit -m "feat: seal Radar Station VNext package manifest"
```

---

### Task 6: Run repository-level qualification and verify the exact source cut

**Files:**
- No new source file required unless a discovered deterministic defect requires correction.
- Read: approved spec, VNext package, manifest, current branch head, comparison against `main`.

**Interfaces:**
- Produces: exact repository-source qualification result only.
- Does not produce native Project behavioral qualification.

- [ ] **Step 1: Run focused package tests**

```bash
python -m pytest -q tests/radar/test_radar_station_vnext_package.py
```

Expected: PASS.

- [ ] **Step 2: Run the existing Python suite**

```bash
python -m pytest -q
```

Expected: PASS, or document any pre-existing/environmental failure with exact evidence instead of weakening tests.

- [ ] **Step 3: Re-render the manifest and prove clean determinism**

```bash
python scripts/render_radar_station_vnext_manifest.py
git diff --exit-code -- project/radar-station-vnext/v1/RADAR_STATION_INSTALL_MANIFEST.json
```

Expected: no diff.

- [ ] **Step 4: Verify scope against `main`**

Inspect the branch compare and require changes to be limited to the approved design/plan, VNext package subtree, VNext validator script/test, and later coordination metadata. Any unrelated source change is a blocker.

- [ ] **Step 5: Record exact source-only classification**

The report must use a bounded status equivalent to:

```text
PACKAGE_CREATED
SOURCE_VALIDATED
NATIVE_INSTALL_CANDIDATE
NATIVE_INSTALL_APPLIED = NO
BEHAVIORALLY_QUALIFIED = NO
PATRICK_ACCEPTED = NO
ACTIVE = NO
```

Do not advance native/install/qualification states from repository tests.

---

### Task 7: Freeze the candidate and hand it to Radar and Brigit for hostile review

**Files/Effects:**
- Create draft PR from `work/hephaestus-radar-station-vnext-project-20260908` to `main` only after Task 6 passes.
- Append one Hephaestus Bus message on current `bus/hephaestus-v3` with exact branch/head/spec/plan/package paths and executed tests.
- Do not merge.

**Interfaces:**
- Radar reviews Bus/runtime/currentness claims and any collision with canonical contracts.
- Brigit reviews cross-estate semantics, social usability, voluntariness, zero-cost discipline, and anti-bureaucracy behavior.
- Patrick retains install/cutover/merge authority.

- [ ] **Step 1: Fresh-read exact branch and writer-lane heads**

Before any non-idempotent write, read both the VNext branch head and `bus/hephaestus-v3` head. Abort/reconcile on unexpected divergence.

- [ ] **Step 2: Open a Draft PR**

Title:

```text
Radar Station VNext: progressive-disclosure native Project package
```

Body must state: source-only candidate; zero-cost hard gate; exact ten native source files; no native install/provider effect; focused/full test evidence; request Radar + Brigit hostile review; Patrick retains merge/install/cutover authority.

- [ ] **Step 3: Send the exact-cut Bus handoff**

The message must include the frozen commit SHA, tree if available, PR number, package path, manifest path, spec path, plan path, test commands/results, and explicit non-effects.

- [ ] **Step 4: Verify the Bus append and Draft PR readback**

Fetch both after creation. Branch existence, PR existence, and Bus message durability prove only those bounded effects; do not claim Radar/Brigit consumption until reply/review evidence exists.

- [ ] **Step 5: Stop before protected effects**

No merge, native Project install, source replacement, Supabase mutation, provider deployment, billing/settings change, or activation occurs in this plan.

---

## Plan Self-Review Result

- Spec coverage: all approved sections are mapped to Tasks 1-7, including Brigit's six refinements, the exact ten-file native source set, zero-cost, role separation, degraded modes, release separation, hostile semantics, and anti-bureaucracy.
- Placeholder scan: no implementation `TBD`/`TODO` steps remain.
- Type/property consistency: JSON keys used by tests are fixed in Tasks 3 and 5; native source filenames are identical across tests, manifest renderer, and package topology.
- Scope: one cohesive Project-package subsystem; live/native/provider cutover is deliberately excluded as a later separately authorized stage.
