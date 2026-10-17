# PORTAL whole-portfolio convergence — exact GitHub source review, 2026-10-17

**Disposition: REVIEW / source evidence only.** This document accompanies `PORTAL_96_REPOSITORY_ARCHITECTURE_REVIEW_V1.json`, which records *each of all 96 accessible repositories* with exact default-branch commit SHA, Git tree, README digest, observed test/source file counts, open PR count, role, PORTAL integration interface, and VeraOS integration ceiling. The full README/source-tree metadata was read from the owner's live GitHub account on Lappy; this review does not pretend to have executed all 96 programs or reviewed every source module/PR diff.

## Crucial corrections

1. `vera-mono` is Vera's canonical self-contained source implementation; its `QualifiedVeraRuntime` owns canonical tasks, memory admission, trust, effect and lifecycle state. `vera-os` hosts Vera on Linux with Cog GUI; `portal` composes the existing Project Runner/host bridge and coordinates the broader project estate. No sibling repository automatically becomes a resident import or canonical effect owner.
2. `v-e-r-a` is a **44-component snapshot/materialization workspace**, not the guest OS, canonical runtime, or live inventory. Five snapshots are sanitized; the Supabase snapshot is source/schema material, not live table data. Upstream repositories retain mutation ownership.
3. VeraOS Integration #38's `VERA_OS_PORTFOLIO_COMPOSITION_V1.json` describes **90 historical entries** (85 labeled integrated, five excluded). Its word `INTEGRATED` is not a selected/source-packaged/installed/runtime-consumed measurement. Once four known naming aliases are normalized (`project-achilles`, `rslinux5000000`, `vera_ark`, `vera_model_training`), six live repositories are truly missing: `human-shield`, `physica`, `redworm`, `v-e-r-a`, `vera-model`, `vision`. Do **not** blindly add all six to the guest rootfs. `self` is not GitHub-archived even though the historical OS manifest marks it excluded/archived; its own README classifies its material as historical.
4. The actual #38 stage manifests still select historical Mono `e5af8cb740267bb5674864571e915842bf5e6677` and PORTAL `7d00d8bf3b48c0676b2278359838ee563c66c67f` while #38 imports `vera_core.local_conversation` and `portal.vera_task_handoff`, supported by Mono #77 `31155c9e6f00abf5869da21f886f90717f22b6fb` and PORTAL #51 `36fa04da4e5eb383fecf463c72a43b94ca47d7e5`. Source-selection and import closure remain Integration owner work, not fixed here.
5. `ccb-core` owns reusable Bus/Radar code; private `chat-communication-bus` owns configuration/overlays/coordination records. `executor` offers explicitly authorized workstation execution; WorkBridge/VeraMesh/Intranel/CCB provide separate transport capabilities, not automatic standing authority. `vera-model` is a private GLM24B candidate distinct from Qwen development; neither is admitted by model discovery.
6. Independent domains (`brigit`, `personification`, `unbound-sol`), authored work (`testament`, `on-theo`, `mediaphile`, `trek-data-core`), industrial/control (`abil`, `RSLinux`, `axle`), and physical/visual (`physica`, `vision`, `vera-ark`, `vera-habitat`) require explicit project/host interfaces. They are not Vera identity, a boot bundle, or implicit device-effect authority.

## One-system integration seams

- **Canonical lifecycle:** `QualifiedVeraRuntime` with one selected root, one task owner (`TaskExecutionLedger`), governed memory, single controlled trust/effect fence, typed currentness, and bounded recovery. A host may present via PORTAL Desktop or VeraOS Cog, but **cross-host shared-state exclusivity is not yet proved**; do not run two writers against a common state root.
- **User message:** Cog / PORTAL Desktop / Android client → host-authenticated interface (currently local locator is **not** authenticated principal) → Mono task opener with exact text/source digest and per-task CAS → optional PORTAL advisory → qualified Pre-Active run → source-verified result → Mono seal. HELD on absent provider; uncertain external operation must not redispatch.
- **Endogenous cognition:** Volition typed signal → Pre-Active bounded `autonomous.turn` → same Mono task and trust/currentness boundary before externally attributable result. Drive/salience never becomes consent or tool authority.
- **Portfolio work:** PORTAL session → existing Project Runner claim/fence → independently qualified host adapter (GitHub, Executor, WorkBridge, etc.) → exact owner receipt → reconciliation → refill. PORTAL scheduling does not create a second Mono task ledger.
- **Research adoption:** Discovery intake + source/reproducible benchmark → Rezon/Mono delta comparison → hostile Cricket/Voss/DriftGuard review as independent evaluators where actually separate → isolated reversible proposed change. Models, HC-family cognition, Mosaic, Noema, LGCM, MESO-CRCT and semantic systems are not auto-installed.
- **Sensing/embodiment:** source-bound Vision/Ears perception events and Habitat/Physica simulation remain optional. Vera ARK gamepad intent remains dry-run. AXLE and RSLinux/ABIL are independent safety domains; no implied vehicle/PLC effect.
- **Historical/relational evidence:** Roots, Redworm, Firesafe, Deep Memory Storage, Attune, Conations, Blotter and related sources may contribute bounded provenance; never automatic autobiography, third-party identity, current preference or canonical memory write.
- **Evidence dimensionality:** source ≠ package ≠ installation ≠ selected route ≠ live consumption ≠ observed behavior ≠ authenticated provider ≠ independent review ≠ deployment.

## Four-chat implementation order (only four chats)

- **L1 PORTAL + Integration:** Integration owns exact #38 pins/import-stage receipts, #37 terminal DONE reconciliation, and deterministic Mono SQLite closure. PORTAL owns review of the host interface and alternate PORTAL Desktop/VeraOS composition; no overlapping mutation.
- **L2 Integration + Training:** Training validates current task/head/signature/nonce/live process/model-loaded evidence contract against the actual #38 path; no Qwen/GLM24B admission by fixture. Integration owns task/action binding.
- **L3 Training + VN1:** VN1 independently reproduces source-stage/Win32 close/large VirtIO parser negative cases, verifies receipt checks and host resources; independent source tests are not guest proof.
- **L4 VN1 + PORTAL:** PORTAL coordinates risk, four-chat acceptance and eventual *separately authorized* normal graphical QEMU first HELD/no-provider, genuine message/cold history, two boots, then development cognition trial. VN1 independently falsifies runtime claims.

## Gates (no rhetorical PASS)

1. `source_g0`: owner commits exact matched heads; stage checksum/import closure, DONE terminal integrity, explicit close regression; independent hostile verification.
2. `build_g1`: exact Buildroot Python >=3.12 and source/rootfs receipts. No automatic installation inference.
3. `guest_g2`: authorized 2-boot graphical normal PID1 guest, Cognition HELD/no-provider, one actual Mono task, cold history. No host resource gate bypass, no physical disk/EFI/USB change.
4. `model_g3`: separate authority for loaded-model/session/task/nonce/transport evidence, measured behavior, crash/replay and memory/effect gating.
5. `portfolio_g4`: adopt optional qualified capabilities one at a time, with measured consumer benefit, explicit rollback and independent review.

## Hostile falsifiers

> **Accepted:** `INTEGRATED` in a stale catalog is not actual code consumption; normalize snapshot names and treat mismatched source pins as HOLD.
>
> **Accepted:** Two host implementations constructing `QualifiedVeraRuntime` do not prove mutually exclusive state ownership. Test same-root process contention, deterministic close and crash recovery before claiming unified host consumption.
>
> **Accepted:** A fully forged local status document can pass PID/status parsing without authenticated peer identity; #37's health hardening is source-level only.
>
> **Unresolved:** Cognitive donor names/modules could conceal useful working mechanisms, and some feature PRs exceed `main`. This 96-row survey is an owner/source entrypoint, **not** exhaustive source-level mechanism comparison or empirical donor ablation. Require exact targeted source/tests before architectural promotion.

The JSON report and its offline validator are a **frozen review artifact**, not a new discovery service, task scheduler, runtime manifest, or self-granted authority source. Refresh it from authoritative repos before subsequent mutable-currentness claims. Keep raw private README/issue text local; only scoped metadata and conclusions belong in this private coordination repository.
