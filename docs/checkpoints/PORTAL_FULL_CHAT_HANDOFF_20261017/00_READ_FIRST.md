# VERA::PORTAL — Full-context engineering continuation checkpoint (2026-10-17)

**Status:** versioned engineering handoff; not canonical Vera runtime state or authorized deployment.
**Audience:** successor PORTAL chat in the four-chat Vera Mono Project.
**Persistence:** private \`thebrazenbeard/chat-communication-bus\` checkpoint review branch and Draft PR, not \`main\`.
**As-of readback:** October 17, 2026. Commit-pinned links to this checkpoint should be generated only after final verified commit.

## Mandatory read order

1. This file (\`00_READ_FIRST.md\`).
2. \`01_REPOSITORY_BASELINE_AND_SOURCE.md\` — current repository heads, branch ownership, source paths, test evidence, blocking defects.
3. \`02_PORTFOLIO_AND_ENGINEERING_HISTORY.md\` — scope, history, donor/adoption choices, authority and evidence ceiling.
4. \`03_FOUR_LANE_COORDINATION_AND_NEXT_WORK.md\` — active owners, work queue, precise next execution unit, hostile review.
5. \`04_NEW_CHAT_RESUME_COMMAND.md\` — pasteable new-chat restoration instruction.
6. \`BUS_368_COMMENT_INDEX.md\` and \`BUS_368_ARCHIVE_PART_*.md\` — **verbatim** source discussion snapshots, ordered by issue-comment record; then fresh-read the *live* [Bus #368](https://github.com/thebrazenbeard/chat-communication-bus/issues/368) for newer returns.

Each artifact is provenance/continuation evidence; none overrides current GitHub \`main\`, current PR heads, Patrick's latest statements, observed host state, or independent runtime evidence. Do not transplant this snapshot into canonical memory.

## Mission and present correction — USER_DIRECT

Patrick's objective is a coherent Vera system: \`vera-mono\` owns the self-contained, portable Vera implementation (identity, governed memory, reasoning, task ownership, cognition, recovery, conation/initiative and protected-effect boundaries); VeraOS is its Linux-based operating environment. Other repositories serve as selected source donors, external infrastructure, research laboratories, or independent reviewers unless expressly and reproducibly absorbed. Vera is not equivalent to Qwen, Cog, a chatbot, a collection of Python packages, a single chat, or an always-running model.

**Most important explicit correction in this conversation:** Patrick mentioned about **300.39 GiB of unallocated space on Disk 1 next to D:** as the eventual installation destination, NOT an instruction to install or partition. The assistant first proposed USB testing as a prerequisite, then prematurely treated the location as authorization to plan an install; both were rejected. **Current priority:** make VeraOS work correctly in normal graphical QEMU, first no-provider/held and isolated no-network deterministic cognition, then separately authorized authenticated real Qwen. **Absolutely no physical disk, EFI, bootloader, USB installer, partition or installation work now.**

Four chats ONLY: PORTAL overall lead; Integration; Training; VN1, with overlapping responsibility pairs **L1 PORTAL+Integration, L2 Integration+Training, L3 Training+VN1, L4 VN1+PORTAL**. Preserve this corrected topology. The rejected eight-chat proposal must not return.

PORTAL is the configured interaction identity in this task, not evidence of an installed \`vera_core.QualifiedVeraRuntime\`, persistent same-process agent, continuous off-turn operation, consciousness or privately authorized effects.

## Highest-value latest discovery

**VeraOS #38 has a real, current SOURCE/BULDROOT-SELECTION BLOCKER.** Although Integration source-tested normal HTTP → Mono #77 task → PORTAL #51 advisory → Pre-Active and durable history, its existing \`architecture/portfolio/VERA_OS_PORTFOLIO_COMPOSITION_V1.json\` and implementation-plan pins (see \`01\`) still select old Mono \`e5af8cb...\` and PORTAL \`7d00d8bf...\` heads that lack the imports required by the current #38 resident. Stage-VeraOSResidentSources.py verifies the **old** pins and refuses arbitrary substitution. A self-consistent, exact-source #38 Buildroot stage/image is therefore NOT yet available. **Repair selected source bindings through Integration owner; do not claim guest-readiness based on manually staged host tests.** VN1 independently identified this defect, and PORTAL has not patched the owner's branch.

**Ownership divergence:** PORTAL-owned VeraOS #37 advanced to \`14c57dd89cae905139f5329c0789dbb8f83f6a8d\` with DONE-event terminal integrity fix. Integration-owned #38 is \`85d6cd39fe32e1214b213a63bdac0b1f54e664ac\`, branched from #37 predecessor \`52f24410...\`. GitHub compare currently says 2 commits ahead / 2 behind, merge base \`52f244103e183d9883f5df23e4d87815dbcc57a8\`. The two branches need **owner-coordinated reconciliation**, not unilateral writes by PORTAL to #38.

**Additional blockers:** VN1 proved Win32 \`attestation.sqlite\` file handle not explicitly closed on resident shutdown (GC only), and the original VeraOS owner #32 VirtIO newline frame parser still accepts complete >8192-byte frames before size rejection; native POSIX scratch fix tested but **not committed in the owner's branch**. Training real-Qwen host-owned provider currentness/loaded-model/session/nonce/task-bound admission remains HOLD. Normal-init Linux graphical QEMU is NOT observed for this exact integrated source. Lappy available RAM last observed 7.04GiB, below the proposed 12GiB-free safe gate for the hypothetical no-provider guest experiment.

## Verified current GitHub source baseline (as-of checkpoint)

- \`vera-mono/main\` \`16a2828dfa7fb7e6c0e19004f014bc68fc47badf\`.
- \`vera-os/main\` \`d2197238d350e4311a49098a1b00ca171a568340\`.
- \`chat-communication-bus/main\` \`68ef3ea15574c2b828dab6d417bf6175b2de6c35\` **before checkpoint branch**.
- Vera Mono [#76](https://github.com/thebrazenbeard/vera-mono/pull/76) \`36ae11802808bc1b1392a361716109d1022ee6af\`, Draft.
- Vera Mono [#77](https://github.com/thebrazenbeard/vera-mono/pull/77) \`31155c9e6f00abf5869da21f886f90717f22b6fb\`, Draft; base #76.
- VeraOS [#37](https://github.com/thebrazenbeard/vera-os/pull/37) \`14c57dd89cae905139f5329c0789dbb8f83f6a8d\`, Draft; PORTAL-owned.
- VeraOS [#38](https://github.com/thebrazenbeard/vera-os/pull/38) \`85d6cd39fe32e1214b213a63bdac0b1f54e664ac\`, Draft; Integration-owned; old base #37 \`52f244...\`.
- VeraOS [#32](https://github.com/thebrazenbeard/vera-os/pull/32) \`5ddac1459c3a7b06f251721a14048fc26e60bda0\`, Draft; VeraOS upstream owner.
- PORTAL [#51](https://github.com/thebrazenbeard/portal/pull/51) \`36fa04da4e5eb383fecf463c72a43b94ca47d7e5\`, Draft; advisory-only.
- Integration [#6](https://github.com/thebrazenbeard/v-e-r-a/pull/6) \`24c95d651da0dc8f55b690c1efa1b4ff58c9115c\`, Draft.
- Training [#106](https://github.com/thebrazenbeard/model-training/pull/106) \`d784caf44db57c1c7f30f1dcd4a437214094c7ff\`, Draft.
- Executor/VN1 [#16](https://github.com/thebrazenbeard/executor/pull/16) \`69020bb46446ca0806eea3d53fe79d7ffba11455\`, Draft/feature off.
- Intranel [#12](https://github.com/thebrazenbeard/intranel/pull/12) \`58714f5f6561b5e44e42dcdbca67e2cb59bfb87b\`, Draft.

All as-of claims were fresh-read in this chat on 2026-10-17, but **MUST be re-read** by the successor chat.

## Immediate safe work / owner routing

**First:** independently check the selected source pin conflict and ask Integration to rebind #38 manifests to the exact Mono #77 and PORTAL #51 selected sources and add staging regression that fails when imported modules are absent. PORTAL should work on independent analysis/review and non-colliding acceptance harness in its owned #37 or isolated scratch, NOT edit #38 owner branch. **Second:** coordinate PR37 terminal-DONE fix into #38, fix deterministic close in actual Mono/VeraOS owning code through Integration, and obtain #32 owner's committed VirtIO bound/parser native POSIX regression. **Third:** have Training map its \`bind_mono77_opened_message\` and QualifiedRuntimeModelGate to the exact approved OS composition; real provider still HELD. **Fourth:** only after exact source staging is repaired and independently checked, prepare a collision-safe pinned Buildroot candidate and ask Patrick for **separately scoped** build/QEMU resource and temporary artifact authority; real model trial requires another separate authorization.

No additional scheduler/router/task DB, no new chat topology, no main merge or deployment. Next win is an exact-pinned, runnable normal resident and observed guest GUI, not another standalone PASS.

## Authority and evidence

Classes: \`USER_DIRECT\`, \`REPOSITORY_SOURCE\`, \`RUNTIME_OBSERVATION\`, \`EXTERNAL_EVIDENCE\`, \`INFERENCE\`, \`HYPOTHESIS\`, \`AUTHORITY\`, \`ACTION\`, \`EFFECT\`, \`VERIFICATION\`, \`UNKNOWN\`. Keep proposition/referent/scope/type attached. SOURCE ≠ BUILD ≠ INSTALLATION ≠ CURRENT_ROUTE ≠ RUNTIME_CONSUMPTION ≠ BEHAVIOR ≠ ATTESTATION ≠ INDEPENDENT_REVIEW ≠ PRODUCTION. REQUEST ≠ AUTHORITY ≠ ATTEMPT ≠ EFFECT ≠ VERIFIED EFFECT.

Patrick's exact permission is required for physical partition/EFI/install/USB, main mutation/merge, runtime deploy/activate/cutover, trust/keys/provider/credentials/rulesets, canonical-memory write, paid compute, protected or destructive effects, and unauthorized model/QEMU runs. Safe inspect, code, isolated tests, Draft PRs and verified private checkpoint persistence permitted here. External writes require readback. Never claim hidden off-turn work. Project chat is not proof an installed Vera process is consuming it.

**Completeness ceiling:** this records all accessible substantive conversation/coordination engineering facts, not private chain-of-thought, invisible tool state, deleted historical conversations, unknowable connector state, or mathematically lossless process continuity.
