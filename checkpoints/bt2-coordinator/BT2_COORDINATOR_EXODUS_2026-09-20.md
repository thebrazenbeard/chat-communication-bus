# BT2 Coordinator Exodus Recovery Checkpoint — 2026-09-20

checkpoint_id: BT2_COORDINATOR_EXODUS_2026-09-20
status: STARTING_SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT
future_interface_owner: BT2 Coordinator
chat_dependency: false

## Purpose

This checkpoint retires the current ChatGPT execution terminal without making the conversation a recovery dependency.

The persistent human interface topology remains exactly:
1. Vera
2. Vera Control Plane Coordinator
3. BT2 Coordinator

Worker identities, specialist roles, assignments, authority, currentness, and project state must be reconstructed from durable Git/Bus/provider evidence. A temporary ChatGPT/Work/API/CLI/model/subagent execution context is a terminal, not durable identity or memory.

No ChatGPT conversation URL, title, ID, hidden state, browser tab, or continued access to the retiring conversation is required by this checkpoint.

## Scope of this retiring terminal

This conversation historically served two durable functions:

1. Masa specialist execution for debugging/root-cause/reliability and hostile review.
2. BT2 Coordinator execution for current Exodus reconciliation.

The Masa portion is already separately evacuated and remains durable at:
- checkpoint: checkpoints/masa/MASA_EXODUS_2026-09-20.md
- checkpoint blob observed in final audit: 8b51bab7acb641548dd035fd8b4aa4cf50f15620
- successor correction: messages/0023-masa-exodus-r51-subject-correction.md
- message blob observed in final audit: 639e0dfa15d03ee1c45c86309779e41854654f1a

Do not reconstruct Masa from this conversation. Use the durable Masa checkpoint/lane plus fresh source evidence.

## Canonical repositories and exact source snapshot

### Build Team Two
Repository: thebrazenbeard/bt2
Canonical branch: main
Observed main:
- commit 30e81cadd94fae117a7f6875523c03251c7c9f6e
- tree 6782a2d62afeab8cefb1a3bc39cc39ab617d637c

### Chat Communication Bus
Repository: thebrazenbeard/chat-communication-bus
Observed default main:
- commit aeab0f04fc9b4bd7c2945c9a53011c53fac809b4

Current topology source:
- architecture/contracts/RADAR_TOPOLOGY_V1.json on Bus main
- current protocol branch bus/protocol-v2
- integration branch radar/control-plane-v1
- current ACTIVE writer routes include One, Two, Three, Four, Five, Five-Five, Six, Seven, Eight, Nine, Thirteen, Masa, Mune, Hephaestus, Radar, Vera, Yin, Yang, FNG, and Brigit; Parallax remains REGISTERED_INERT.

Fresh-read topology before every future writer-lane write.

## BT2 Exodus reconciliation — current candidate

Preferred BT2-local consolidation surface:
- PR #35
- branch exodus/bt2-role-interface-reconciliation-v1-20260920
- exact head ea0fcea92d829ee4a79628f8e50f31783d65b4ea
- base main@30e81cadd94fae117a7f6875523c03251c7c9f6e
- state OPEN / DRAFT / UNMERGED

PR #35 reconciles the following earlier candidates:
- PR #24 — BT2 Coordinator interface surface
- PR #26 — exact 13-role reconstruction/source map
- PR #27 — exact three-interface topology and coordinator recovery contract
- PR #29 — audit/checkpoint provenance, not normative topology
- PR #34 — Eight chat-era loader compatibility note, now carried into PR #35

Normative topology result on PR #35:
- exactly 13 BT2 role-source members:
  one, two, three, four, five, six, seven, eight, nine, thirteen, masa, mune, hephaestus
- Seven source:
  archive/training-sources/project-achilles/seven/v1.0.0
- exactly three persistent interfaces, in order:
  Vera
  Vera Control Plane Coordinator
  BT2 Coordinator
- PR #24 compatibility files are explicitly adapters to the normative contracts, not a second topology authority.

Eight correction:
- docs/exodus/BT2_EIGHT_CHATLESS_RECONSTRUCTION_COMPATIBILITY_20260920.md is now present on PR #35.
- frozen Eight v1.0.0 chat-era loader bytes remain historical source and were not rewritten.
- Eight reconstruction does not self-award BASE_READY/qualification/install/activation.

Verification ceiling:
- fresh structural readback established exact role count = 13 and exact interface count = 3 before the Eight compatibility carry-forward.
- the Eight carry-forward changes documentation only.
- no hosted workflow run was returned for PR #35 exact heads during this terminal.
- therefore PR #35 status is SOURCE_CANDIDATE / STRUCTURAL_READBACK, not hosted-CI PASS, installation, activation, behavioral qualification, merge, or deployment.

### Independent BT2 policy frontier

PR #23 remains a separate candidate:
- title Add BT2 adversarial collaboration posture
- head 22a0053df845113fbdce00433ceff44844f5a80b
- base current main
- state OPEN / DRAFT / UNMERGED

Do not silently fold PR #23 into Exodus topology/reconstruction semantics.

PR #23 changes the BT2-wide proposal-evaluation/collaboration layer and includes a V4 Project package/install candidate. It must be reconciled separately, with Project installation and behavioral qualification kept distinct from source acceptance.

Classification:
- PR #23 = IDEA/SOURCE POLICY CANDIDATE / INDEPENDENT FRONTIER
- PR #35 = CURRENT EXODUS TOPOLOGY/RECONSTRUCTION CONSOLIDATION CANDIDATE

## External PR mirror

BT2 PR #35 is mirrored on the Bus:
- Bus PR #147
- branch mirror/bt2-pr35-exodus-reconciliation-20260920
- exact head 6c6401905146c80c92c7f21bafe165ab021f5783
- base Bus main
- state OPEN / DRAFT / UNMERGED

Source PR #35 remains canonical for the BT2 changes. Bus PR #147 is communication/mirror evidence only.

## Bus Exodus integration and issue #142

Historical input:
- Bus PR #128 supplied the three-interface Exodus topology semantics.

Current active Exodus integration candidate inspected by this terminal:
- Bus PR #140
- title Exodus: reconcile runtime recovery and complete worker census 20/20
- exact head 2461df3a1a8393d4c7ded227afb17ecc7abfacb3
- state OPEN / DRAFT / UNMERGED

Do not design current runtime changes against PR #128 or default main alone when PR #140 remains the fresher integration subject.

### Runtime-instance fencing gap

Bus issue #142 remains OPEN:
- Exodus: fence concurrent runtime instances for one durable worker assignment

Observed architectural seam:
- durable assignment ownership is identity-level through assignee_identity_id;
- runtime/node liveness is node-level through node_id plus heartbeat/lease;
- current source does not bind one assignment execution generation to one live runtime instance.

This is a collision/stale-worker problem, not a user-authority problem.

Source-only design candidate:
- Bus PR #146
- branch exodus/assignment-runtime-fencing-design-v1-20260920
- exact head 13350bbf6767c54e291e0c4c5e41b2d1c8bc9a92
- exact parent PR #140 head 2461df3a1a8393d4c7ded227afb17ecc7abfacb3
- state OPEN / DRAFT / UNMERGED
- exactly three added source files
- no SQL migration

PR #146 freezes:
- durable worker identity != runtime/node identity;
- one current assignment execution claim per assignment;
- node id plus monotonically comparable fencing token;
- exact assignment-event binding;
- claim lease cannot exceed node lease;
- identity match, node liveness, and dependency-readiness requirements;
- stale node/token/event rejection;
- idempotent operation-id semantics;
- append-only generation/audit requirement;
- execution claim never creates merge/deploy/provider/credential/protected-effect authority;
- service-role-only boundary for any future mutation functions;
- 14 hostile cases frozen before implementation.

Evidence ceiling for PR #146:
- GitHub Actions run 35504940278 reported failure conclusion;
- both Python matrix jobs had steps=[] and runner_id=0;
- classification is HOSTED_CI = NO_RUN / UNKNOWN;
- it is neither semantic FAIL nor PASS;
- source/design readback is established;
- no runtime installation/provider effect exists.

No implementation migration should be written until the design receives independent review and RED hostile cases are frozen against the exact implementation parent.

No future migration may be applied to a provider without separate current authority.

## Lantern

Exact Lantern target remains:
- WoWSQL project bt2-479e4ad9

During this retirement/final qualification sequence, exact-target WoWSQL access failed internally before a canonical V3 projection preflight could be established.

Therefore:
- LANTERN_CURRENTNESS = UNKNOWN
- Lantern was not successfully consulted for the final retirement cut
- no Supabase, Git, Project-file, historical-material, or memory fallback is valid for Lantern currentness
- retry exact V3 preflight -> B0 -> payload -> B1 before any future Lantern-dependent currentness claim

## Chat-dependency audit

BT2 default-branch code search returned no current chatgpt.com, main-chat, or fresh-chat operational dependency.

Bus main still preserves historical chat/session-oriented wording in old recovery/design provenance, including historical Radar recovery material. Those files are not to be rewritten merely to erase history.

Current Exodus integration work (PR #140 and associated reconstruction contracts) is the intended runtime-neutral successor: worker/runtime reconstruction must not depend on a permanent worker conversation.

Historical chat links or chat-era wording may remain provenance, but must not be required current-state locators or authority sources.

No Slack reconnection/configuration was performed. Slack remains outside current durable coordination architecture unless separately authorized.

## Classification of state from this terminal

ALREADY_DURABLE:
- current BT2 Project Instructions V3 and source/runtime boundaries;
- Bus protocol/topology;
- 13 preserved role-source packages;
- prior Masa hostile review/recovery state;
- source PRs, reviews, issues, and exact-head evidence.

NEW_DURABLE_VALUE:
- PR #35 consolidated topology/reconstruction candidate;
- explicit Seven repair in coordinator reconstruction;
- Eight chatless compatibility carry-forward into PR #35;
- Bus PR #146 runtime-instance fencing design + hostile matrix;
- Bus PR #147 mirror of BT2 PR #35;
- this coordinator recovery checkpoint.

SUPERSEDES_EXISTING:
- permanent worker-chat assumptions are superseded by role reconstruction from durable source/state.
- Bus PR #128 is historical/provenance input for Exodus topology; PR #140 is the fresher integration subject inspected for current Bus design.

HISTORICAL_EVIDENCE:
- PRs #24/#26/#27/#29/#34 remain preserved exact-head source/history even where PR #35 consolidates their useful Exodus content.
- Bus chat-era recovery prose remains historical evidence.

IDEA_OR_FUTURE_FRONTIER:
- BT2 PR #23 adversarial-collaboration policy/V4 package.
- Bus issue #142 implementation beyond the design-only PR #146.

CONFLICT:
- no unresolved 13-role vs three-interface conflict remains in PR #35.
- source/build/install/behavior states remain intentionally separate.
- Lantern currentness remains UNKNOWN, not conflicted/promoted.

PRIVATE_OR_OUT_OF_SCOPE:
- Patrick personal/health/family/relationship/sexual/autobiographical material was not copied into project repositories.

## Authority ceiling

This Exodus work authorized reversible repository/source/checkpoint/review work only.

Not authorized and not performed:
- merge;
- canonical promotion;
- production deployment;
- provider/database mutation;
- credential or permission mutation;
- destructive deletion/rewrite;
- force push;
- paid infrastructure;
- visibility/publication change;
- model training;
- ChatGPT Project Settings mutation;
- canonical-memory mutation;
- Slack reconnection/configuration;
- installation/activation effects not already separately authorized.

## Reconstruction test

A fresh BT2 Coordinator runtime can recover without this conversation by reading:
1. installed current Project Instructions;
2. bt2/main and current open BT2 PRs, especially #35 and independent policy PR #23;
3. Bus current topology and active integration PR #140;
4. Bus issue #142 and design PR #146;
5. Bus mirror PR #147;
6. current Bus recovery checkpoints, including Masa's checkpoint when Masa is dispatched;
7. exact provider readback only when available and authorized.

From those surfaces it can determine:
- what BT2 Coordinator is;
- the exact three-interface topology;
- the 13-role reconstruction map;
- current open Exodus source candidates;
- what is source-only vs tested/installed/runtime;
- the unresolved independent-review/CI/provider gates;
- protected-effect authority limits;
- where to write future durable results.

No archived chat is required.

## Exact next coordination frontier

Future interface:
BT2 Coordinator

Exact directive:

BT2_COORDINATOR::EXODUS_RESUME::FRESH_CHECK_PR35_PR146_PR23_AND_BUS140::VERIFY_EXACT_HEADS::OBTAIN_INDEPENDENT_REVIEWS::NO_MERGE_NO_PROVIDER_MUTATION

Required sequence:
1. fresh-check bt2/main and PR #35; if head still ea0fcea92d829ee4a79628f8e50f31783d65b4ea, obtain independent architecture/reconstruction review and real executable validation of the topology validator before promotion;
2. keep PR #23 separate and reconcile its V4 policy/install package independently;
3. fresh-check Bus PR #140, issue #142, and PR #146; if exact head 13350bbf6767c54e291e0c4c5e41b2d1c8bc9a92 remains current, obtain independent hostile/design review and execute its contract tests in a real runtime;
4. only after design approval may a source-only fencing implementation branch be created with RED hostile cases;
5. do not apply any provider migration or merge without separate current authority;
6. retry Lantern only through exact WoWSQL target bt2-479e4ad9 when Lantern currentness matters; fail closed if unavailable.
