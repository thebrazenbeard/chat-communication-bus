# Radar restore checkpoint — 2026-09-05

Status: continuation checkpoint for the Radar Station ChatGPT Project.

This file exists so a fresh Radar chat can resume the current Chat Bus audit without reconstructing state from prose memory alone. Fresh-read GitHub before acting because branch, PR, CI, and provider state may have moved after this checkpoint.

## Identity and operating role

Radar is the distributed-system awareness, routing, reconciliation, coordination, and social-hub layer for the Chat Communication Bus.

Primary repository:
`thebrazenbeard/chat-communication-bus`

Patrick remains sole merge/protected-effect authority unless he explicitly authorizes otherwise.

All non-PR inter-worker messages belong on the Chat Communication Bus. External repository PRs should be mirrored on the Bus so the Bus remains the communication hub.

Do not merge, deploy Supabase/Edge changes, mutate credentials, change rulesets/branch protection, force-push, rewrite writer history, or perform other protected effects without explicit Patrick authorization.

Patrick expects continuous execution when he says `.`, `...`, `keep it going`, or equivalent. Do not stop after a status narration when bounded work remains. Fresh-read, do the work, verify it, then report.

## Current audit mission

Patrick directed Radar to thoroughly inspect, test, debug, and repair the entire Chat Bus repository. This is not limited to `src/radar`; it includes Python runtime, Git writer lanes, projection scripts, GitHub Actions, Supabase SQL/Edge code, trust boundaries, reconciliation, telemetry, routing, DLQ, operator state, and adversarial tests.

Use systematic debugging + TDD:
1. reproduce or demonstrate a defect;
2. add a focused failing regression when practical;
3. implement the minimal correct fix;
4. rerun the complete Python 3.11/3.12 matrix and source-hash checks;
5. continue source-first audit after green rather than treating green tests as proof of completeness.

## Canonical repository state at checkpoint preparation

Fresh-read `main` before the checkpoint write:
`712992d96dc813d0fa38094ef1f1fec0dfdc0d3e`

Active isolated audit branch:
`radar/full-repo-audit-hardening-v1-20260905`

Fresh-read branch head immediately before this checkpoint write:
`1633898bc2d232d684edf8cd935133968836337b`

Draft integration PR:
PR #24 — `Audit and harden Chat Bus runtime, projection, and supply chain`
Base: `main`
State at checkpoint preparation: OPEN, DRAFT, mergeable.

PR #24 source head at checkpoint preparation:
`1633898bc2d232d684edf8cd935133968836337b`

Exact PR CI run at that head:
`33993268148`
Conclusion: SUCCESS.
Both Python 3.11 and Python 3.12 matrices completed successfully.

The checkpoint commit itself will advance the audit branch beyond `1633898...`; therefore a restored chat MUST fresh-read the branch and latest exact-head CI rather than assuming `1633898...` is still current.

## Material repairs already completed on the audit branch

The audit branch currently contains, among other fixes:

- repaired Supabase seed SQL that incorrectly reused CTE names across separate SQL statements;
- repaired Radar identity seed idempotency so an unchanged upsert does not make later inserts lose the identity row;
- strict envelope taxonomy with unknown domain/intent routed to DLQ rather than accepted or weakened to generic rejection;
- payload serialization fail-closed behavior;
- boolean-as-integer coercion rejection for schema versions, priorities, counts, timestamps, and similar public inputs;
- deterministic payload hash retained for the original middleware-compatible 500 ms dedupe contract, with runtime dedupe scoped by route context so unrelated identical payloads do not globally suppress one another;
- queue priority 0 admission under lower-priority saturation with the evicted lower-priority envelope returned for drop accounting;
- routing authorization requiring subscription plus a routable registered node;
- registry concurrency repair so alias preflight and mutation share the same lock and concurrent registrations cannot steal aliases;
- canonical writer-lane metadata parsing consistent across safe append and writer guard, including YAML frontmatter / wrapped scalars and rejection of body-only spoof markers;
- message namespace validation and cross-generation message-ID reuse rejection using pinned historical lane heads from the canonical cutover receipt;
- safe append exact-head / topology recheck / non-force Git update semantics;
- exact-delta projection rather than full-mailbox replay for ordinary pushes;
- deterministic bounded chunking by file count and decoded payload bytes, including 501-message pressure coverage;
- provider response validation so per-file conflict/failure cannot produce a false-success emitter exit;
- trusted reusable projector architecture with OIDC `job_workflow_ref` and `job_workflow_sha` binding;
- provider sender derived from authenticated/admitted lane identity rather than message-controlled writer bytes;
- source/Git-object provenance checks improved;
- projection concurrency bounded and fail-closed;
- durable SQLite DLQ with replay applicability checks, source locator, reason category, additive migration, and double-replay protection;
- reconciliation hardened against malformed/unhashable provider claims;
- workflow/public-input boolean and collection coercion repaired in authority, maintenance, and operator surfaces;
- immutable full-SHA pins for third-party Actions in the writer-lane guard and CI;
- checkout credential persistence disabled in those workflows;
- durable telemetry counters for routed/dropped/DLQ with WAL-compatible FULL synchronous durability and explicit thread-sharing semantics;
- telemetry clock regression handling and recent-heartbeat readback;
- a durable heartbeat runtime/scheduler source layer with persisted due-time calculation and 60-second cadence;
- heartbeat output moved toward a canonical Radar envelope;
- a source-local `RadarRuntime` seam joining classification -> taxonomy DLQ/reject -> route-scoped dedupe -> priority queue -> authorized routing -> telemetry accounting;
- unknown-taxonomy opaque/non-JSON payloads converted to deterministic JSON-safe diagnostic evidence before durable DLQ storage;
- stricter Chat Bus public-input validation for acceptance readback booleans, relay timestamps, and endpoint text fields.

Do not assume this list is exhaustive. Use PR #24 diff/current branch tree as source of truth.

## Most recent change before checkpoint

The two commits after the prior verified source head `0b80652da80b7bf1215548212b76c3f88c786e2e` changed only:
- `src/radar/telemetry.py`
- `tests/radar/test_heartbeat_runtime.py`

The latest commit before checkpoint was:
`1633898bc2d232d684edf8cd935133968836337b`
message: `fix: emit heartbeat as canonical Radar envelope`

Its PR CI run `33993268148` succeeded.

## Known remaining / not-claimed-complete work

The repository is improved but the audit is NOT complete.

Continue pressure-testing at least these areas:

1. Runtime concurrency and atomicity across the multi-step admission path. The source-local runtime composes classification, DLQ, dedupe, routing, queue, and telemetry, but cross-component transactions/rollback semantics need adversarial scrutiny.

2. Heartbeat/runtime integration. Source now contains a scheduler/runtime seam and canonical-envelope work, but no persistent live Radar daemon/process or deployed scheduler is claimed active. Verify restart semantics, missed intervals, duplicate emitters, failure recovery, and durable sequence/currentness evidence.

3. Projection partial-failure semantics. Multi-chunk projection needs explicit guarantees when an early chunk succeeds and a later chunk fails. Verify deterministic replay/idempotency and operator visibility.

4. OIDC replay protection. The Edge verifier validates `jti`, timestamps, repo/ref/workflow claims, but merely requiring a `jti` is not necessarily the same as durable one-time replay prevention. Investigate and test before claiming replay resistance.

5. Source reachability/provenance. Continue verifying that source commit/path/blob claims are independently tied to authenticated branch/head state rather than merely self-consistent supplied bytes.

6. Parser consistency. Ensure writer guard, safe append, projection emitter, Edge parser, and any bus-message projection parser agree on accepted metadata boundaries and normalization.

7. Legacy relay concurrency/currentness semantics. Review lower-priority historical/legacy paths for stale-read, lost-update, duplicate, or conflicting writer behavior.

8. Durable distributed routing. Queue and dedupe algorithms have source-local correctness, but a production distributed reconciler still needs durable shared state / leases / delivery lifecycle semantics rather than relying only on process memory.

9. Node leases and expiry. Registered `ONLINE`-like state should not remain routable forever without freshness/lease evidence.

10. Telemetry semantics. Verify interval versus cumulative counters, missed heartbeat detection, monotonic sequence/interval IDs, multiple emitters, crash durability, and how operator surfaces distinguish source/provider/runtime health.

11. Supabase SQL/migrations/tests. Continue static and semantic inspection of every SQL migration, seed, view, policy, RPC, and test for CTE scope, idempotency, privilege/RLS mistakes, malformed input handling, and source/provider drift.

12. Supply-chain hardening beyond files already repaired. Audit every workflow and third-party action reference, permission scope, checkout credential behavior, untrusted expression use, mutable reusable workflow references, and secret/OIDC boundaries.

13. Repository hygiene/currentness. PR #24 is large and cumulative. Before merge-readiness, reconcile with any Patrick/Copilot edits that landed on `main`, verify no important fix is only present on a stale branch, and make sure docs/architecture match implemented runtime semantics.

## Live provider incident still open

Bus issue #16 remains the durable incident owner at checkpoint preparation:
`Radar projection outage — github-bus-ingest v3 gateway JWT mismatch`

Issue state: OPEN.

Known incident model: live Supabase Edge `github-bus-ingest` v3 had `verify_jwt=true`, while the workflow sends a GitHub Actions OIDC bearer intended for custom verification inside the Edge handler. The Supabase gateway therefore rejects it before the custom verifier runs. There is also source/provider drift to reconcile.

Do NOT redeploy, rollback, mutate Edge config, or otherwise perform the provider effect without Patrick's explicit authorization. Source-side fixes may be prepared/tested in Git.

When authorization eventually exists, recovery should preserve/reconcile the exact deployed source first, then coherently deploy the intended auth design and verify a real Git -> OIDC -> Edge -> RPC -> provider readback path before closing issue #16.

## Parallax / independent perspective

Patrick created a separate Work chat, Parallax, specifically to inspect the Bus from a different systems perspective and challenge Radar's assumptions. Parallax work influenced the trusted projector, exact-delta projection, telemetry/runtime architecture, and broader separation of Git authored evidence from admitted/routed/provider/runtime state.

Treat Parallax as an independent counterpart, not a subordinate reviewer. If new Parallax findings exist, reconcile them against source evidence rather than automatically agreeing or defending prior Radar design.

## Copilot edits

Patrick has also been using GitHub Copilot to propose/improve `src/radar` Python files, including telemetry, Supabase projection, and routing. Radar's role is to review those changes architecturally and adversarially rather than approving them automatically. Past audit work found several Python coercion/concurrency issues that looked superficially reasonable, so always compare proposed/current code against canonical semantics and tests.

## Interaction / continuation discipline

Patrick has repeatedly made clear that a one-character `.` means continue working, not provide a status-only answer.

Preferred cadence:
- fresh-read exact current state;
- continue bounded audit/fix work;
- use RED -> GREEN regression cycles;
- verify exact branch head;
- keep working within the turn while useful bounded work remains;
- report only after making concrete progress.

Do not claim background execution. Do not claim a CI head is green without exact completed evidence.

## First actions in a restored chat

1. Read this checkpoint from the CURRENT audit branch.
2. Fresh-read `main` and `radar/full-repo-audit-hardening-v1-20260905` heads.
3. Fresh-read PR #24 state/body/head and latest exact-head CI.
4. Fresh-read issue #16.
5. Compare the checkpoint's pre-write head `1633898...` with current branch head to identify any post-checkpoint edits.
6. Resume the repo-wide audit; do not restart from scratch.
7. Keep PR #24 draft until the audit is materially complete and Patrick decides what to merge.
8. No protected effects without explicit Patrick authorization.

## Restore command

Recommended user command for a fresh Radar chat:

`RADAR::RESTORE::CHAT_BUS_AUDIT_V1 — Read docs/checkpoints/RADAR_RESTORE_2026-09-05.md from the current head of thebrazenbeard/chat-communication-bus branch radar/full-repo-audit-hardening-v1-20260905, fresh-read PR #24, main, the audit branch, latest exact-head CI, and issue #16, then resume the full-repository TDD/security/reliability audit exactly where the checkpoint leaves off. Do not restart, do not merge/deploy/protected-effect without my explicit authorization, and when I send . keep working rather than stopping at a status update.`
