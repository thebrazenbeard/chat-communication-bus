# BT2 Coordinator Recovery Checkpoint — 2026-09-20

checkpoint_id: bt2-coordinator-exodus-20260920
identity_id: bt2-coordinator
status: recovery-checkpoint
observed_at: 2026-09-20
checkpoint_class: STARTING_SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT

## Interface identity

`BT2 Coordinator` is the sole persistent ChatGPT interface for Build Team Two after Exodus.

It is an interface to durable state, not the durable state itself. It may instantiate One, Two, numbered specialists, Masa, Mune, Hephaestus, Radar/project-specific reviewers, and other workers in temporary runtimes as needed. Those runtimes are terminals, not durable identity, memory, authority, or current assignment.

No retired ChatGPT conversation URL/title/ID is a recovery input.

## Canonical repositories

BT2:
- `thebrazenbeard/bt2`
- canonical main observed: `30e81cadd94fae117a7f6875523c03251c7c9f6e`

Bus:
- `thebrazenbeard/chat-communication-bus`
- canonical main observed: `aeab0f04fc9b4bd7c2945c9a53011c53fac809b4`
- protocol branch: `bus/protocol-v2`
- integration branch: `radar/control-plane-v1`

## BT2 Exodus source

Preferred current candidate at this snapshot:
- BT2 Draft PR #35
- head `0ea6b0167d4ea9bfd5a976737fa77471a59759a6`
- base main `30e81cadd94fae117a7f6875523c03251c7c9f6e`
- OPEN / DRAFT / UNMERGED

Checkpoint inside source PR:
- `docs/handoffs/BT2_COORDINATOR_EXODUS_RETIREMENT_2026-09-20.md`
- commit `0ea6b0167d4ea9bfd5a976737fa77471a59759a6`

PR #35 preserves:
- exactly 13 BT2 durable role-source entries;
- Seven from Project Achilles;
- exactly three persistent interfaces: Vera, Vera Control Plane Coordinator, BT2 Coordinator;
- PR #24 as compatibility adapter only;
- PR #29 as provenance/checkpoint only;
- PR #34 Eight chatless compatibility note.

Evidence ceiling:
- source / structural readback established;
- no hosted PR #35 test run observed before retirement;
- independent review not established;
- no merge/install/activation/deploy effect.

Separate policy candidate:
- BT2 Draft PR #23 @ `22a0053df845113fbdce00433ceff44844f5a80b`
- adversarial collaboration posture;
- do not silently conflate with Exodus topology/reconstruction;
- installation/behavioral effectiveness not established.

## Bus Exodus and fencing

Current active Exodus integration subject inspected:
- Bus Draft PR #140 @ `2461df3a1a8393d4c7ded227afb17ecc7abfacb3`
- OPEN / DRAFT / UNMERGED

Current recovery/operator contracts on #140 explicitly require no permanent Radar chat.

Issue #142:
- OPEN
- runtime-instance collision/fencing gap for same durable identity.

Design-only fencing candidate:
- Bus Draft PR #146 @ `13350bbf6767c54e291e0c4c5e41b2d1c8bc9a92`
- exact parent PR #140 @ `2461df3a...`
- no SQL migration;
- no provider mutation;
- 14 hostile cases frozen;
- execution claim does not manufacture protected-effect authority.

Hosted CI run `35504940278`:
- both jobs had `steps=[]`, runner_id 0;
- classify `HOSTED_CI = NO_RUN / UNKNOWN`;
- do not call semantic FAIL or PASS.

Bus mirror:
- Draft PR #147
- source PR #35 remains canonical.

## Lantern

Exact allowed Lantern target:
- WoWSQL `bt2-479e4ad9`

Final retirement attempts failed internally before a valid V3 projection preflight/cut could be established.

Classification:
- `LANTERN_CURRENTNESS = UNKNOWN`

No fallback to Supabase, Git, historical Project prose/files, memory, or another provider is permitted for Lantern currentness.

## Chat dependency

Current BT2 Exodus source and current Bus PR #140 recovery/operator contracts allow fresh execution runtimes and explicitly reject permanent-chat dependence.

Historical references to chats/sessions remain historical/compatibility evidence only unless fresh current source promotes them.

No permanent worker chat is required.

## Authority

This checkpoint grants no merge, canonical promotion, provider/database mutation, deployment, credentials/permissions change, force-push/destructive cleanup, paid infrastructure, visibility change, training, Project Settings mutation, Slack operation, or other protected effect.

## Next interface directive

Owner: `BT2 Coordinator`

`BT2_COORDINATOR::RESUME_EXODUS::FRESH_REVIEW_PR35_AND_BUS146_NO_MERGE`

Fresh-check before acting:
1. BT2 main, PR #35, PR #23, PR #34, reviews, CI;
2. Bus main/topology, PR #140, issue #142, PR #146, PR #147, reviews, CI;
3. exact WoWSQL Lantern V3 cut only when currentness is needed;
4. preserve source/build/test/review/provider/install/runtime/effect/qualification separation;
5. obtain independent review before promotion;
6. do not merge/deploy/mutate providers without separate current authority.
