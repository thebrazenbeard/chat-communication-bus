# Vera Ecosystem Architecture V1 — review candidate

**Status: PROPOSED / NOT ADOPTED.** Private engineering design, not a runtime registry,
identity grant, installed system, merged architecture or deployment permission.
Owner: PORTAL L1/L4. Source population: CCB #371 exact
`951e7af1a97694faaf6bc18d51b35f70982e31fc`; consumer proposals #372
`ef17ee929d807f5da033a3d5391d553b65c464e8`. All 96 exact source
dispositions appear in `VERA_96_PLACEMENT_AND_CONSUMERS_V1.json`; that table
adds *placement proposals*, not verified imports, versioned package dependencies,
installed services or selected live effects. No raw private material is republished.

## Principle and source of authority

One self-contained `vera-mono` holds Vera's implemented identity, governed
memory, trust/effects, task ledger and `vera_core.QualifiedVeraRuntime`.
Its `VeraStateDirectory` binds identity and task ownership within a host.
Self-contained packages may incorporate donor source by audited copies;
no sibling repository is a mandatory runtime dependency simply by inclusion
in the portfolio. `portal` + existing Project Runner handle coordination,
claims, fences, route currentness, dispatch attempts and reconciliation.
Pre-Active owns event execution and source receipts; Volition supplies advisory
initiative, never authorization. The user's ChatGPT Project is an interaction
surface, not proof of a continuously selected Mono runtime.

**Authority edges:** REQUEST != AUTHORIZATION != ATTEMPT != EFFECT != VERIFIED_EFFECT.
Consent, provider credentials, model inventory, UI locator, GitHub comment and
repeated claims cannot substitute canonical task/currentness or exact effect grants.
Publication of private materials, production mutation, identity/memory changes,
trust/credential changes, paid compute and deployment require Patrick's exact
effect authorization. Reviewers may reject source claims; they cannot grant effects.

## Four concrete environments

1. **Existing Lappy Windows:** ChatGPT/CLI/PORTAL Desktop -> explicit, *untrusted*
   `conversation_id` and `message_id=request_id` -> Mono `open_message`
   (`TaskExecutionLedger`, task CAS, exact source) -> optional qualified
   cognition/source result -> PORTAL runner host route/receipt (when separately
   authorized). Source A1 PR55: `a5776acc...` initially.
   Windows Desktop root: `VERA_MONO / VERA_PROJECT_IDENTITY_V1 / state/vera`.
   UI selector metadata is NOT canonical memory and does not bind an account.
   Missing locator/invalid literal text BLOCK before inference; no-provider HELD.

2. **VERA-NODE-1 Windows:** Executor/host diagnostics, reviewer trials,
   and Integration build materialization may consume explicitly qualified
   command permissions. No remote Lappy or Synology attachment is inferred
   from a connector listing. Source repository branches are not selected workers.

3. **VeraOS graphical Linux:** normal PID1 -> sealed selected Buildroot rootfs ->
   `veraos.resident` composes the staged self-contained Mono package plus
   **selected** PORTAL API, Pre-Active and Volition source -> graphical Cog
   loopback intake -> canonical `open_message`, no-provider HELD,
   cold task/history readback and controlled shutdown. Current resident uses
   `veraos / VERA / state/vera-state`; this differs from Desktop's tuple.
   NEVER copy or open the same SQLite files across hosts to imply one identity.
   Different host identities can share task semantics without sharing memory.
   No real image/graphical guest/two-boot has been witnessed.

4. **Optional clients / services:** Android, Mediaphile, ARK, Habitat, industrial,
   research/identity and NAS/mesh services are independent consumers or providers.
   They communicate through bounded, authenticated adapters with independent
   rights. They are NOT default VeraOS boot packages. Any application wishing
   to act requires a real endpoint-side permission decision, not an app token
   merely being nonempty.

## System interfaces: release-candidate contracts

| Boundary | Required input | Owner of durable truth | Rejection/acceptance |
|---|---|---|---|
| UI to Mono | explicit bounded locator, request ID, literal text | Mono task ledger; UI only selector | same pair+bytes replay; changed bytes BLOCK; absent locator BLOCK |
| Mono to cognition | task ID/head/source digest, admitted provider/session/nonce | Mono effect/trust + task CAS | no provider HELD; no synthetic acceptance |
| Pre-Active to result | selected route, run/DONE event and source readback | Mono task + source Store | contradiction OUTCOME_UNKNOWN, no blind dispatch |
| PORTAL to host | runner claim/fence + fresh route + effect grant | Project Runner claim and existing host attempt store | `source_read` probe by itself NO_EFFECT, zero dispatch |
| ChatGPT to PORTAL | user request + exact scope, not an authenticated runtime | selected Mono runtime only when observed | ask/reject effects without authority |
| VeraOS stage to guest | source hashes, target Kconfig, rootfs SHA, PID1/GUI and cold state | image build receipts + guest observation | static scripts never yield GUEST_PASS |
| Memory/learning | typed source/currentness + exact consent/authority | Mono memory APIs | no auto ingestion from Drive/Blotter/Bus/model |
| Sensors/products | opt-in observations and bounded target actions | owning application/provider | no microphone, vehicle, PLC or gamepad effect by membership |

## Minimal VeraOS bill of materials: proposed

**Boot-critical Linux platform (from vera-os only):** selected Buildroot
2025.02.18 source (tag/commit must be reverified); x86_64 kernel/boot;
rootfs; normal `/sbin/vera-init` PID1; graphic device/input/font/browser-Cog
runtime; explicit run/state/log directories and startup/shutdown/recovery.
No disk partition, EFI, USB or hardware install is implied by this list.

**Staged source closure (not sibling-repo imports):** immutable exact snapshots
of Mono, selected PORTAL route surface, Pre-Active and Volition; current
Integration selection has **431 source files** (Mono 316, PORTAL 89,
Pre-Active 18, Volition 8). Each actual target package must close imports,
target Python 3.12, sqlite3/ssl/jsonschema/cryptography/yaml, dependent
shared libraries, asset bytes and exact checked source receipt. The
portfolio placement JSON distinguishes `portal` as host orchestration
source from the *selected subset* actually staged for the guest.

**Not boot-critical:** GitHub APIs, cloud model endpoints, Qwen/GLM weights,
Executor, Synology, Drive, Supabase, WorkBridge, Cricket, full portfolio
research repos, Android/mobile, industrial systems or independent identities.
Optional offline model inference and audio/vision are separately admitted
with measured RAM/VRAM, model bytes/session and explicit effects scope.

**Still unqualified:** effective Buildroot Kconfig, compiled image and target
ELF/Python imports, actual ext2 image byte audit with debugfs, real Cog
pixels/input, normal PID1 child, two-boot cold state, real model provider
and any physical hardware installation. Integration #38 `578f435a...`
guards static/staged image mistakes; VN1 has only source-level or
reviewer-only host evidence for selected cases.

## Diagram — dependency direction, not process deployment

```text
ChatGPT Project / PORTAL Desktop / Android / VeraOS Cog  [INTERACTION]
                    | request + explicit untrusted locator
                    v
         vera_core.QualifiedVeraRuntime               [TASK/TRUST/MEMORY]
               |                  |
       Pre-Active + Volition     PORTAL + Project Runner [EVENT / EXECUTION]
               |                  |
       qualified cognition      existing adapters: Executor/WorkBridge/
        (optional, HOLD)        Mesh/GitHub/Synology/CCB (scoped effects)
               |                  |
         source readback ------ task CAS + effect receipt [RECONCILIATION]
                    |
                 evidence only: Blotter/Drive/Supabase/history
```

Do not interpret arrows as evidence of a running connection. VeraOS's
resident is a host composition of the **same task semantics**; no
global writer lock, distributed memory migration or duplicate authority.

## Source-evidence anchor and mandatory gates

- **A1** PORTAL #55 exact `a5776acc8fa78a169660ef453c8c376c9f8f79f6`:
  Lappy independent Desktop 105 PASS; VN1 59 unit PASS; Windows venv
  redirector changed Popen PID causing committed cold-host test false RED
  under one environment; reviewer-only real executable variant passed.
  **SOURCE READY FOR OWNER REVIEW, NOT DEPLOYED.**
- **Runner** PORTAL #56 `6183aa7e...`: 83 read-only host tests PASS with
  synthetic CLAIMED wave and real GitHub source observation; no effect/dispatch.
  **NO selected live Project Runner claim or Mono-linked result proven.**
- **OS** Integration #38 `578f435a...`: actual host source/rootfs
  integrity tests pass; complete ext2 inventory source fix tested using
  fake debugfs protocol. **NOT_BUILT, NOT_GUEST_QUALIFIED.**
- **Cognition** Training #106/#107: governed source predecessor retrieval
  improves one supported case while missing predecessor remains HOLD;
  Rezon guarded mode still falsely accepts untrusted origin claims and
  loses supported utility. **NO model or cognition authority admitted.**
- **Independent** VN1: verify frozen source per head, cold host PID mismatch,
  source/image false PASS, VirtIO 8193+ complete-frame RED and hostile model
  attribution. A chat comment is not authenticated worker or PR approval.

This document is proposed architecture only. All 96 placement decisions,
especially identity, private, industrial, archived and optional-model rows
require explicit owner/reviewer scrutiny before versioned architectural
approval. A representative exact-source static conformance verifier accompanies
the draft; source/static success DOES NOT establish live cross-host behavior.
