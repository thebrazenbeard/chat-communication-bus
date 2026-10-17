# 02 Unresolved architecture decisions, reviews, and exact next work

**READ AS OPEN DECISIONS, NOT CURRENT APPROVAL.** Re-check Bus #368 after
latest receipt `6235315822`, and newer PR heads before any owner mutation.
Use the existing four pair lanes; no fifth native governance chat.

## P0 — VeraOS Cog reply-attribution RED (Integration-owned #38)
VN1 on Integration #38 `beef4a6d...` read actual browser Cog
`sendMessage`: source UI may retire an untrusted pending selector after
an HTTP `status='BLOCKED'` and `task_id='ui-...'` without verified
same conversation/message/literal/source/head acknowledgment. Reviewer-only
source JS gave **8 PASS / 1 RED** on fabricated
`ui-fabricated-no-source-proof`. This establishes a client retry/source
binding defect, NOT an independently exploitable guest or Mono ledger write.
**Owner:** Integration repairs actual Cog in existing #38 only.
**Independent:** VN1 reproduces new exact head negative and cold replay.
**Acceptance:** no pending removal unless a bound server-side canonical
acknowledgement matches the original request and state; ambiguous
outcome retained/NO_REDISPATCH; source/no-provider and browser tests GREEN.
PORTAL must not modify #38. No real browser pixels/boot claimed.

## P0 — Codex A1 #55 newest Windows cold test
Previous #55 `a577...` had 105/105 independent Lappy Desktop focused
PASS; independent VN1 found test harness virtualenv redirector
`Popen.pid != real resident heartbeat.pid`, not demonstrated app defect.
Codex A1 source has NOW advanced to `2f42d494...` with PID harness fix.
**Owner:** same ONE existing Codex conversation, no second worker.
**Acceptance:** fresh exact-head independent original Windows host and
cold test on VN1 + Lappy, typed journal/source/cold response, zero model,
source identity, process handle release; original test must pass without
reviewer-only modifications. Broader source suite retains existing
#52 GitHub CLI discovery failure in recorded evidence; distinguish baseline
failure from newly introduced failure. Current installed Desktop unchanged.

## P0 — Six-node false-hard-dependency cycle, 96 dispositions
Independent VN1 source graph found 147 PROPOSED consumer edges and
a six-node cycle `portal/vera-mono/vera-os/vera-apk/model-training/executor`
*only when those edges are interpreted as hard runtime imports*.
The portfolio overlay is not a call graph. **PORTAL/Integration** must
type actual observed interfaces/consumer/advisory/donor vs real stage/import/
selected process and test no circular boot closure before declaring V1
accepted. 90 historic VeraOS source composition entries / 44 V-E-R-A
snapshots do not make 96 installed/boot-critical guest packages.
**Acceptance:** exact symbolic imports/packaging and manifest/test sources
for each actually boot-selected edge; independent false-hard-cycle test.

## P1 — No-provider semantics, state-root lifetime and graph
Mono #77 is canonical task authority; PORTAL A1 requires explicit UI
untrusted locator, message_id=request_id, exact original text; no provider
=> Mono `TASK_OPENED/PENDING_NO_ADMITTED_PROVIDER` and presentation HELD.
OS #38 internal default `veraos-local-console` and HTTP `BLOCKED`
without model differs at UI boundary. Owner contribution explains common
underlying Mono semantics but does not prove same presentation.
Integration should define explicit typed projection, local-console scope
and external Cog source attribution, and test deterministic closes.
Current normal guest is Linux `veraos/VERA`, Windows Desktop remains
`VERA_MONO/VERA_PROJECT_IDENTITY_V1`; never merge roots/identity or
SQLite writers by source similarity. Existing Windows source tests passed
5 actual host/resident conformance; not target Linux qualification.

## P1 — Real minimal graphical guest bill of materials
Current staged 431 files: Mono316/PORTAL89/PreActive18/Volition8.
This is ACTUAL selected source-stage prototype, not proof all are strictly
necessary for a hypothetical minimal no-provider guest. Integration
owns true package closure: Buildroot 2025.02.18 effective .config / target
Python3.12/ELF dependencies, actual ext2 member and byte audit, PID1→
resident child, DRM/Cog pixels/input and two clean cold boots. Separate
resource gate, and explicit Patrick authorization before QEMU/model/physical
installation or heavyweight build. No GUI or loaded model as of handoff.

## P1 — Cognitive/source provenance
Training #108 introduced typed cognitive capability interface, 63 source
tests PASS; no loaded model/issuer-owned attestation. Rezon guarded mode
still 3/10 unsafe false ANSWER and two false abstains; REJECT automatic
provenance admission. Missing predecessor/source remains HOLD.
Training should review #373 exact BOM for cognitive *required* vs optional
features, source lineage, no-provider offline core, model memory feasibility
Lappy 32GiB/4GiB VRAM, and return one concrete negative/positive test.
VN1 independently attempts to counterfeit receiver-owned source.

## P1 — Host orchestration not yet live-qualified
#56 real read-only GitHub GET + *synthetic* claimed wave, fake authority
NO_EFFECT and zero dispatch was actually source-tested. NO verified
canonical Mono-selected live Project Runner claim/effect execution path;
host currentness ≠ authority. PORTAL next smallest owned work is a
read-only bounded `canonical task -> claim/fence -> exact probe -> HOLD/
NO_EFFECT -> reconciliation` conformance, using EXISTING Project Runner
and PORTAL host bridge. If no real task authority/claim exists, preserve
SOURCE_ONLY hold; do not invent it or build new scheduler.

## P1 — Upstream VirtIO parser
OS upstream #32 unchanged `5ddac145...`: POSIX socketpair complete
8193+ frame can be accepted/JSON before bounds denial. Preserve true
RED and ask exact upstream owner to fix; VN1 independently re-tests
8191/8192/8193/split/frame and provides logs. Do not mix with
Integration #38 or unapproved actual QEMU run.

## Owner returns needed to accept V1
- Integration: exact #373 review ACK/CHALLENGE against its source BOM
  contribution, terminal/locator/PID1/Cog semantics and real image gates.
- Training: source-only and cognition capability acceptance/rejection,
  no self-attested cognition/provider origin as authority.
- VN1: source-level graph/packaging/Cog/false-PASS criticism and
  independent conformance, not another coder on owner branches.
- PORTAL: records survived/rejected objections, versioned amendments on
  noncolliding private Draft; *no claim of all-role signoff* until readback.
- Codex: one serial bounded implementation packet **after** owner contract,
  no competing architecture/control plane.

**Immediate new PORTAL chat:** Read full checkpoint and fresh Bus; if
owner-review changes occurred, classify them first. Resume actual work
rather than only reorienting. Use newly agreed interface to select one
bounded implement/test task; do not collide with active Cog or Codex A1.
