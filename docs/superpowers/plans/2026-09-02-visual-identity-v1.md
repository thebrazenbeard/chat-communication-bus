# Visual Identity V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fail-closed repository-native visual identity registry, standardized Bus avatar style contract, initial Radar portrait custody, and lightweight Supabase projection.

**Architecture:** Git profiles and vendored assets are canonical. `src/radar/visual_identity.py` validates profile semantics and resolves renderable assets without allowing association to become identity proof. Supabase stores metadata only and can be rebuilt from Git.

**Tech Stack:** Python 3.11+, standard library (`dataclasses`, `enum`, `hashlib`, `json`, `pathlib`), pytest, PostgreSQL/Supabase SQL.

**Spec:** `docs/superpowers/specs/2026-09-02-visual-identity-v1-design.md`

## Global Constraints

- Visuals belong to logical identities, never sessions/endpoints/transports.
- House style target is 85% human / 15% stylized.
- Candidate rendering requires explicit opt-in and visible candidate state.
- Git is canonical; Supabase is derived and stores no image bytes.
- Do not invent another identity's visual claim.
- A visual-profile failure must not invalidate Bus identity/lane health.
- Radar's existing portrait digest is `37e64e7375ea68fadf0905654dbf82ce04a309faa1a7e191399904eb5e8e59dc`.

---

### Task 1: Profile model and semantic validation

**Files:**
- Create: `src/radar/visual_identity.py`
- Create: `tests/radar/test_visual_identity.py`

**Interfaces:**
- Produces `VisualIdentityError`, `VisualAsset`, `VisualProfile`, `load_visual_profile(path)`, `validate_visual_profile(profile)`, and `resolve_bus_avatar(profile, allow_candidate=False)`.

- [ ] **Step 1: Write failing tests** for valid self-canonical portrait, identity/path mismatch, duplicate canonical scope, candidate pointer mismatch, retired current pointer, malformed digest, out-of-scope path, and candidate resolution policy.
- [ ] **Step 2: Run** `python -m pytest -q tests/radar/test_visual_identity.py` and verify RED because `radar.visual_identity` does not exist.
- [ ] **Step 3: Implement the minimal dataclasses/parser/validator/resolver** using standard library only. `resolve_bus_avatar()` must return canonical `bus_avatar`; return an explicitly active candidate only when `allow_candidate=True`; otherwise return `None`.
- [ ] **Step 4: Run** `python -m pytest -q tests/radar/test_visual_identity.py` and the full suite; both must pass.
- [ ] **Step 5: Commit** `feat: add visual identity profile validation`.

### Task 2: Versioned contracts and initial Radar profile

**Files:**
- Create: `architecture/contracts/VISUAL_IDENTITY_V1.schema.json`
- Create: `architecture/contracts/BUS_AVATAR_STYLE_V1.md`
- Create: `identities/radar/profile.json`
- Add binary: `identities/radar/assets/2026-09-02-radar-canon-v1.png`
- Modify: `tests/radar/test_visual_identity.py`

**Interfaces:**
- Consumes Task 1 profile loader.
- Produces a repository-valid Radar profile with portrait scope only; no derived Bus avatar is falsely claimed.

- [ ] **Step 1: Add a failing repository-profile test** that loads `identities/radar/profile.json`, verifies the portrait record is canonical/self-claimed, and verifies asset bytes hash to the declared digest.
- [ ] **Step 2: Run the targeted test and verify RED** because the profile/asset files are absent.
- [ ] **Step 3: Add the JSON Schema contract, style contract, Radar profile, and exact existing portrait bytes.** The profile must declare style contract `BUS_AVATAR_STYLE_V1`, portrait canonical state, and no bus-avatar canonical pointer.
- [ ] **Step 4: Run targeted and full test suites** and verify green.
- [ ] **Step 5: Commit** `feat: register Radar visual identity`.

### Task 3: Supabase metadata projection contract

**Files:**
- Create: `supabase/migrations/20260902_radar_visual_identity_v1.sql`
- Create: `supabase/tests/radar_visual_identity_v1.sql`
- Create: `src/radar/visual_projection.py`
- Create: `tests/radar/test_visual_projection.py`

**Interfaces:**
- Produces deterministic metadata rows for `radar.identity_visuals` and SQL upsert statements/parameters without image bytes.

- [ ] **Step 1: Write failing Python projection tests** proving canonical metadata fields, no binary/body field, stable row identity, and candidate state preservation.
- [ ] **Step 2: Verify RED** because `radar.visual_projection` does not exist.
- [ ] **Step 3: Implement minimal projection serialization** from validated `VisualProfile`/`VisualAsset`.
- [ ] **Step 4: Add SQL migration** for `radar.identity_visuals` keyed by `asset_id`, with identity foreign key, state/scope checks, path/hash/provenance/style fields, timestamps, RLS enabled, and no image/blob column.
- [ ] **Step 5: Add SQL contract tests** checking table/columns, RLS, and absence of byte-storage columns.
- [ ] **Step 6: Run Python full suite**; commit `feat: add visual identity metadata projection`.

### Task 4: Integration verification and provider projection

**Files:**
- Modify docs only if verification reveals an operator-contract gap.

- [ ] **Step 1: Run** `python -m pytest -q` and `python -m compileall -q src`; verify zero failures/errors.
- [ ] **Step 2: Push/observe CI for the exact feature head** and require success.
- [ ] **Step 3: Apply the Git-held Supabase migration** only after exact-head CI succeeds.
- [ ] **Step 4: Project the Radar profile metadata** from Git-held source; do not insert image bytes.
- [ ] **Step 5: Read back `radar.identity_visuals`** and verify Radar portrait metadata, digest, state, and no binary columns.
- [ ] **Step 6: Fast-forward/merge to `main` only if integration is fast-forward-safe or PR checks are green, then run/observe exact-main CI.**
