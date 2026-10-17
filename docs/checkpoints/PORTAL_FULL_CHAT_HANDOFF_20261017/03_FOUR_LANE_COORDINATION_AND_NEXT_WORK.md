# 03 — Four-chat ownership, current returns, next safe work and review

Historical coordination: https://github.com/thebrazenbeard/chat-communication-bus/issues/368. This handoff reads 74 issue comments, reproduced in the BUS_368_ARCHIVE_PART files and indexed separately. GitHub comments are evidence of communication, NOT authenticated acknowledgments by native ChatGPT worker chats. Read live issue for newer comments.

## Exactly FOUR chats and overlapping pairs

PORTAL — overall lead, L1 with Integration and L4 with VN1. PORTAL owns VeraOS Draft #37 at 14c57dd89cae905139f5329c0789dbb8f83f6a8d, normal resident assembly and graphical QEMU acceptance planning. PORTAL does not own Integration OS #38 or Mono #77, VeraOS upstream #32, Training #106 or Executor #16.

INTEGRATION — L1 with PORTAL, L2 with Training. Own canonical Mono task PR #76/#77, OS integration #38, Integration #6 and relevant Intranel #12. Latest #77 head 31155c9e6f00abf5869da21f886f90717f22b6fb; latest #38 head 85d6cd39fe32e1214b213a63bdac0b1f54e664ac. Own task CAS, stable conversation identity, history and source correlation. Source-tested task consumption is not installed guest.

TRAINING — L2 with Integration, L3 with VN1. Own model-training PR #106 at d784caf44db57c1c7f30f1dcd4a437214094c7ff. Own host-model identity, freshness, provider lease/nonce/current task, source cognitive evaluation, Qwen control and donor triage. Real model admission HOLD; current head full test not yet run.

VN1 — L3 with Training, L4 with PORTAL. Own independent reviewer execution and Executor #16 (69020bb46446ca0806eea3d53fe79d7ffba11455, feature off). Independently reproduced actual source/test results and found Buildroot pin conflict, SQLite shutdown lock, guest runner safety and VirtIO parser defect. Independent reviewer must bind exact frozen source+test, not self-assert source success.

VeraOS upstream #32 owner is a separate collaborator, NOT a fifth Vera chat; it owns VirtIO parser. Never edit active owner branches without explicit cancellation/coordination. Eight-chat proposal was explicitly rejected and must not return.

## Latest owner returns (all exact GitHub source comments)

PORTAL: https://github.com/thebrazenbeard/chat-communication-bus/issues/368#issuecomment-6232813172
— #37 terminal DONE fix committed, 19/19 Lappy Windows host tests, latest #77/#38 staged 15/15, #37/#38 2 ahead/2 behind and no normal QEMU.

INTEGRATION: https://github.com/thebrazenbeard/chat-communication-bus/issues/368#issuecomment-6232785160
— Mono #77 + OS #38 fixed raw message-ID collision across conversations, added bounded history, 25/25 latest matched Lappy host source tests, current #38 branch owner active.

TRAINING: https://github.com/thebrazenbeard/chat-communication-bus/issues/368#issuecomment-6232782878
— current #106 binds exact opened Mono77 task to scoped model request, no dispatch authority; latest head tests not fully run; false-HOLD counterexample and real host Qwen evidence HOLD.

VN1: https://github.com/thebrazenbeard/chat-communication-bus/issues/368#issuecomment-6232853745
— separate-node latest matched OS38/Mono77 19/19; two Windows no-model resident child processes yielded nine held/history records, no provider call; exact selected Buildroot old component pins do not contain imported modules; attestation.sqlite deterministic closure RED; PR32 VirtIO native scratch 4/4 but uncommitted; QEMU host resources below proposed free-RAM gate. The full comment contains detailed log hashes, branch names, local scratch archive and precise owner issue links.

INTEGRATION previous real OS37 source join: https://github.com/thebrazenbeard/chat-communication-bus/issues/368#issuecomment-6228322357
— Integration #6 offline-source advisory and canonical task correlation 18/18 Lappy focused; GitHub CI Windows/Ubuntu source jobs success but two new exact private OS tests were SKIPPED in CI.

Find older work and exact original chronological discussions by reading the full archived Bus comments instead of inferring ACKs from the current summary.

## Next smallest safe engineering work unit — PORTAL leads without owner collisions

FIRST: reproduce and report the precise source selection mismatch. Read exact current source-pin manifests in VeraOS #38: architecture/portfolio composition and implementation plan. Read Stage-VeraOSResidentSources.py, the selected Mono/PORTAL source heads and the modules actually imported by resident. Request Integration owner to update the source pins to Mono #77 and PORTAL #51, preserving staged provenance and verifying stage receipt/hash plus absence-of-module RED/now-present GREEN. Reconcile PORTAL #37 new terminal-DONE patch into Integration #38 via owner consent. The GitHub compare is two commits ahead/two behind with merge base #37 predecessor 52f244103e183d9883f5df23e4d87815dbcc57a8. PORTAL must NOT edit the active #38 branch.

SECOND: coordinate deterministic close of Mono QualifiedVeraRuntime SQL handles plus resident finally path. Use Win32 attestation.sqlite rename/rmtree RED from VN1, NOT forced gc.collect. Integration owns canonical Mono changes; PORTAL owns separate noncolliding OS code and can test/peer review. Keep original SQLite state owners; no new journaling system.

THIRD: VeraOS upstream #32 owner commits pre-JSON MAX_FRAME guard and native Linux POSIX regression, preserving 8192 legal and rejecting 8193/8237 complete frames. VN1 verifies exact committed head independently. Matching response ID does not authenticate serving peer.

FOURTH: Training supplies directly resident-consumable host-owned trust gate attached to QualifiedVeraRuntime/outbound registry, exact signed loaded Qwen model/process/session/host/endpoint/current Mono task/nonce. Scoped turn or source fixture alone is no model dispatch permit. Real provider remains HOLD without actual live attestation.

FIFTH: PORTAL composes one source-consistent Buildroot candidate only after owner pins and resource-scoped authority. Prevent fixed-name Docker removal, shared overlays, stale image source, nographic-only renderer in graphical test. Do not borrow old CORE_BOOT image as current RESIDENT_BROWSER evidence.

SIXTH: ask Patrick for a separately scoped normal /sbin/vera-init graphical QEMU no-provider A trial only after safe resource headroom. Desired 4GiB guest/2 vCPU, Docker <=6GiB, host RAM >=12GiB free, no NIC, only isolated owned disposable QCOW2/state/log paths, localhost VNC/QMP and source/image SHA receipts. Previous Lappy free RAM ~7.04GiB so condition not met then; remeasure. B synthetic guest fixture is another controlled milestone (test-only fixture not installed). C real Qwen trial requires independent explicit model/host permission. No QEMU or image build has been executed in this handoff.

## Acceptance assertions

- Exact selected source matches Buildroot component receipt, Mono #77 local_conversation and PORTAL #51 route-advice imports actually present.
- Normal PID1 selects genuine resident; Cog responsive/healthy even with real provider held; no false model qualification.
- UI POST literal task → one canonical Mono TASK_OPENED and task-scoped CAS; independent Pre-Active run/event source evidence; GET history returns exact prior user text with unverified input label and no memory admission.
- FAILED/CLAIMED Pre-Active event with completed run never HTTP200; out-of-window/uncertain inference outcome never silently redispatched.
- No provider authentication or protected effect inferred from localStorage session ID, Origin/Host header, route advisory, ModelResponse fixture, task CAS or SQL evidence.
- Cold QEMU guest reopens actual evidence across two boots before declaring guest qualification. Two Windows child-process tests are lower-level source/process evidence only.

## Hostile review outcomes

Objection: Why not simply make a synthetic fixture return real displayed text and claim working GUI? ACCEPTED AGAINST SHORTCUT. The test process is not a real model identity. #38's current pinned source cannot yet build a self-consistent imported module graph, so image/guest testing would use stale or mismatched code.

Objection: Why not merge all Drafts to main and force source unification? REJECTED AS UNAUTHORIZED. Protected merge needs Patrick's exact permission; branches have active separate owners. Reconcile with review and explicit selected commits.

Objection: Must authentic Qwen admission block no-provider QEMU boot? PARTIALLY ACCEPTED. Real model admission is NOT prerequisite for no-provider UI+canonical task/history verification. Real Qwen must remain HOLD and be a later separately permitted trial.

No new scheduler, task ledger, authority registry, universal message bus, cross-repository runtime dependency or fifth chat. Before every mutation fresh-read exact heads/ownership; after each write read back. No install, physical disk, EFI, USB, real QEMU/model/paid compute or protected effects under current authority.
