# Visual Identity V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fail-closed repository-native visual identity registry, standardized Bus avatar style contract, Radar profile container, and lightweight Supabase projection without fabricating custody of unavailable image bytes.

**Architecture:** Git profiles and vendored assets are canonical. `src/radar/visual_identity.py` validates profile semantics and resolves renderable assets without allowing association to become identity proof. Supabase stores metadata only and can be rebuilt from Git.

**Tech Stack:** Python 3.11+, standard library (`dataclasses`, `json`, `pathlib`), pytest, PostgreSQL/Supabase SQL.

**Spec:** `docs/superpowers/specs/2026-09-02-visual-identity-v1-design.md`

## Global Constraints

- Visuals belong to logical identities, never sessions/endpoints/transports.
- House style target is 85% human / 15% stylized.
- Candidate rendering requires explicit opt-in and visible candidate state.
- Git is canonical; Supabase is derived and stores no image bytes.
- Do not invent another identity's visual claim.
- A visual-profile failure must not invalidate Bus identity/lane health.
- Known digest without repo-custodied bytes is not sufficient to create a current asset record.

---

### Task 1: Profile model and semantic validation

**Files:**
- Create: `src/radar/visual_identity.py`
- Create: `tests/radar/test_visual_identity.py`

**Interfaces:**
- Produces `VisualIdentityError`, `VisualAsset`, `VisualProfile`, `load_visual_profile(path)`, `validate_visual_profile(profile)`, and `resolve_bus_avatar(profile, allow_candidate=False)`.

- [x] **Step 1: Write failing tests** for valid self-canonical portrait, identity/path mismatch, duplicate canonical scope, candidate pointer mismatch, retired current pointer, malformed digest, and candidate resolution policy.
- [x] **Step 2: Verify RED in CI** before `radar.visual_identity` exists.
- [x] **Step 3: Implement the minimal dataclasses/parser/validator/resolver** using standard library only.
- [x] **Step 4: Verify targeted behavior and full suite through branch CI.**

### Task 2: Versioned contracts and Radar profile container

**Files:**
- Create: `architecture/contracts/VISUAL_IDENTITY_V1.schema.json`
- Create: `architecture/contracts/BUS_AVATAR_STYLE_V1.md`
- Create: `identities/radar/profile.json`
- Modify: `tests/radar/test_visual_identity.py`

**Interfaces:**
- Consumes Task 1 profile loader.
- Produces a repository-valid Radar profile container with no current asset until exact image bytes are in Git custody.

- [x] **Step 1: Add repository-profile coverage.**
- [x] **Step 2: Add JSON Schema and Bus style contract.**
- [x] **Step 3: Register Radar's profile container with `current`, `active_candidate`, and `assets` empty rather than claiming a missing repository file.**
- [x] **Step 4: Verify the profile loads and resolves downward to no Bus avatar.**

Radar's separately known portrait digest is `37e64e7375ea68fadf0905654dbf82ce04a309faa1a7e191399904eb5e8e59dc`; it is deliberately not placed in the Git profile until those exact bytes are actually committed and verified.

### Task 3: Supabase metadata projection contract

**Files:**
- Create: `supabase/migrations/20260902_radar_visual_identity_v1.sql`
- Create: `supabase/tests/radar_visual_identity_v1.sql`
- Create: `src/radar/visual_projection.py`
- Create: `tests/radar/test_visual_projection.py`

**Interfaces:**
- Produces deterministic metadata rows for `radar.identity_visuals` and SQL upsert statements/parameters without image bytes.

- [x] **Step 1: Write failing Python projection tests** proving metadata-only rows, stable row identity, and candidate/current state preservation.
- [x] **Step 2: Verify RED in CI** before `radar.visual_projection` and provider migration exist.
- [x] **Step 3: Implement projection serialization** from validated `VisualProfile`/`VisualAsset`.
- [x] **Step 4: Add SQL migration** for `radar.identity_visuals` keyed by `asset_id`, with identity foreign key, state/scope checks, path/hash/provenance/style fields, timestamps, RLS enabled, and no image/blob column.
- [x] **Step 5: Add SQL contract checks** for table, RLS, FK, and absence of binary storage.

### Task 4: Integration verification and provider projection

- [x] **Step 1: Observe exact feature-head CI with Python 3.11/3.12 tests, compileall, and source-hash checks green.**
- [x] **Step 2: Apply the Git-held Supabase migration only after exact-head CI succeeds.**
- [x] **Step 3: Execute provider contract/readback checks.** Current visual row count is correctly zero because no asset bytes have been custodied in Git yet.
- [ ] **Step 4: Fast-forward/merge to `main` only while `behind_by=0`, then verify exact-main CI.**
