# Radar central reconciliation and recovery hardening

Status: approved design, source-only review gate
Date: 2026-09-05
Canonical repository: `thebrazenbeard/chat-communication-bus`
Base reviewed: `main@4205a0e77504d2a127d9996fd54b382d872eff7b`

## 1. Purpose

This design closes the remaining security, reliability, recovery, and currentness gaps found by the full-repository Radar audit after PR #24.

The central failure mode is architectural: writer-lane branches are durable message evidence, but branch-local GitHub Actions currently also act as the projector activation mechanism and as part of the trust boundary. Existing writer lanes retain old workflow files, so merging hardening to `main` does not activate that hardening on those lanes. The live Edge path is separately blocked by Supabase gateway JWT verification and, even if that were corrected, the current source handler depends on an unapplied replay-guard RPC and on reusable-workflow OIDC claims that current lane-local direct jobs do not possess.

This design makes writer branches inert data, moves reconciliation authority to trusted default-branch control code, gives projection an explicit durable journal, repairs migration/recovery provenance, converges parser contracts, and completes Radar Phase 2 at node granularity.

## 2. Non-goals and effect boundary

This spec does not authorize or perform:

- a Supabase migration or Edge Function deployment;
- a provider configuration or secret change;
- branch protection, repository ruleset, billing/visibility, or credential changes;
- force-push, history rewrite, deletion of historical writer lanes, or merge to `main`;
- inference that GitHub branch existence proves ChatGPT runtime liveness;
- automatic activation of a registered but still gated writer lane.

Source implementation, tests, documentation, and a review PR may be prepared after this design review. Every live/provider/protected effect remains separately gated.

## 3. Evidence established by the audit

### 3.1 Branch-local activation is not a trust boundary

Current writer lanes contain older copies of `.github/workflows/radar-bus-projection.yml` and `writer-lane-guard.yml`. They execute the workflow version committed on the pushed branch. The old projector checks out mutable `main`, uses floating third-party action tags, and directly runs the emitter. Therefore the trusted reusable workflow merged to current `main` is source-inert for existing lane pushes.

The default-branch writer guard is useful feedback but is not authoritative because it checks out mutable `main`, and existing lane copies may be stale, removed, or replaced.

### 3.2 Projection outage/backlog is real

The live provider currently contains Radar Bus messages only through `radar-0057`; canonical `bus/radar-v2` contains `radar-0058` and `radar-0059`. The known Edge deployment currently fails GitHub OIDC requests at the Supabase gateway because provider `verify_jwt=true` is inconsistent with the source contract for GitHub OIDC.

The source handler now calls `radar_consume_github_oidc_jti_v1`, but the corresponding replay-guard migration is not live. Provider deployment ordering therefore matters.

### 3.3 Topology registration and active routing are conflated

`RADAR_TOPOLOGY_V1.json` contains Parallax as a required writer lane while its onboarding record still says `TOPOLOGY_PR_PENDING`, `topology_pr_merged=false`, and `first_append_guard_verified=false`. PR #20 actually merged, but the first guarded append has not occurred. Current `load_writer_lanes()` nevertheless treats every `required_writer_lanes` record as active.

A lane must have separate states for reserved/registered and active/current. Presence in the topology registry alone must never authorize projection or coordination.

### 3.4 Phase 2 is not implemented at node granularity

The Python runtime registry is process-local. `Subscription` is identity-level and carries only `domain` plus `min_priority`; it has neither `node_id` nor `intent`. Routing asks whether an identity is subscribed and whether any node for that identity is routable, then returns identity IDs.

The provider schema has durable `nodes` and identity-level `subscriptions`, but the Python runtime does not reconcile to it. Provider `radar.nodes` currently has no routable nodes, so it is not the operating registry today.

### 3.5 Projection can partially commit across files

Each individual `radar.project_bus_message_v1` call is transactional with the receipt and assignment triggers it fires. The Edge handler, however, can project multiple files independently/concurrently. Earlier file transactions can commit before a later file fails. A single per-lane `projected_head` cursor cannot safely represent this condition.

### 3.6 Migration source cannot reproduce provider history

The provider ledger records these already-applied Radar migrations:

- `20260902120716 radar_control_plane_v1`
- `20260902120826 radar_realtime_v1`
- `20260902203610 radar_visual_identity_v1`
- `20260902204759 radar_live_message_projection_v1`
- `20260902231445 radar_live_message_collision_v1`
- `20260903000603 radar_receipt_plane_v1`
- `20260903001906 radar_assignment_plane_v1`
- `20260903113314 radar_operator_views_v1`

Git currently collapses those to repeated `20260902_*` and `20260903_*` prefixes. This loses Supabase migration identity and changes ordering. It can make live projection overwrite collision handling and can omit `identity_visuals` from Realtime during a clean rebuild.

Two later source migrations are not live and must not masquerade as already-applied history:

- thread closure first entered Git at 2026-09-03T21:43:34Z;
- OIDC replay guard entered merged `main` at 2026-09-05T23:26:37Z.

### 3.7 SQL verification and currentness records are not trustworthy enough

The base migration leaves PostgreSQL default `PUBLIC EXECUTE` on `assignment_ready`, `mark_stale_nodes_offline`, and `touch_node`, while the checked-in SQL test asserts no anon/authenticated EXECUTE on any Radar function. Live ACL readback confirms the mismatch. Client roles currently lack Radar schema USAGE, so this is defense-in-depth/invariant drift rather than an exposed PostgREST call.

The Realtime SQL test contains an ambiguous `WHERE pubname = pubname` expression and does not execute successfully. Its expected publication set is also stale: live provider publication includes `messages` and `identity_visuals` in addition to the low-volume control tables.

Normal CI runs only Python tests and hashes two migrations plus one seed. It does not prove the SQL migration chain or execute database assertions.

The current self-registration contract and `radar_v1.sql` still name `bus/radar-v1`; replaying that seed would regress provider currentness. `RADAR_CURRENT.json`, README, Supabase contract, recovery documentation, branch disposition, Parallax onboarding state, and the restore checkpoint also contain stale claims.

## 4. Canonical lane-state model

Topology must explicitly distinguish registry membership from projection eligibility.

Each writer-lane record shall expose a machine-readable lifecycle state with at least:

- `REGISTERED_INERT`: branch/name reserved; no message projection or coordination authority;
- `ACTIVE`: current canonical writer route and eligible for reconciliation;
- `HISTORICAL`: immutable predecessor evidence only;
- `RETIRED`: no new writes; preserved evidence.

Only `ACTIVE` lanes are enumerated by central reconciliation.

Parallax remains `REGISTERED_INERT` until the onboarding sequence records both the merged topology registration and a successful first guarded append. The stale Parallax contract/test must be corrected to factual currentness rather than preserving `TOPOLOGY_PR_PENDING` as a green invariant.

Historical cutover records remain historical evidence. They are not live liveness records and are not projection cursors.

## 5. Central dispatcher and trusted projector

### 5.1 Wake-up paths

A default-branch dispatcher shall have two wake-up mechanisms:

1. `workflow_run` on completion of `Writer Lane Guard` for `bus/**` branches, for low latency.
2. a five-minute scheduled reconciliation backstop.

The writer-branch workflow run is only a hint that a branch may have changed. Its conclusion, artifact, checkout, workflow source, or caller-supplied values are never projection authority.

The scheduled path makes progress even when a writer branch contains stale workflow source, a writer removes/replaces a workflow, or a wake-up is lost.

### 5.2 Never execute writer-branch code

Trusted reconciliation may read Git commits, trees, blobs, and paths from writer branches. It must never execute or source:

- a writer-branch workflow;
- scripts/configuration from the writer branch;
- writer-branch Actions artifacts or caches;
- binaries or generated executable content from the writer branch.

Writer branches are untrusted inert data except for the message content admitted under the canonical grammar.

### 5.3 Immutable control source

The reusable trusted projector must be established at immutable commit `A`. It checks out control source from its own immutable workflow SHA/repository identity, not mutable `main` and not the target writer lane.

A later dispatcher/caller commit references the reusable workflow by exact commit `A`. This two-commit release pattern avoids a self-referential pin.

Third-party Actions must use immutable commit SHAs and checkout credentials must not persist unless a narrowly documented write requires them.

## 6. Durable reconciliation journal

### 6.1 Why a journal, not only a cursor

A lane head can contain several commits; a delta can contain several files; a request can contain several chunks; and individual file projections can commit before the batch is complete. Therefore durable state must distinguish observation, validation, projection progress, and final advancement.

### 6.2 Proposed provider state

Add rebuildable operational tables conceptually equivalent to:

`radar.projection_lane_state`

- `lane_identity` primary key
- `branch_name`
- `admitted_head_sha` nullable
- `projected_head_sha` nullable
- `last_observed_head_sha` nullable
- `state` (`UNINITIALIZED`, `READY`, `RECONCILING`, `DIVERGED`, `BLOCKED`)
- claim owner/token + claim expiry
- timestamps and diagnostic metadata

`radar.projection_batches`

- deterministic batch id
- lane identity
- base/projected cursor at start
- target head
- topology/control source SHA
- state (`PLANNED`, `VALIDATED`, `PROJECTING`, `COMPLETE`, `FAILED`, `DIVERGED`)
- chunk count / completed chunk evidence
- exact error/replay state
- created/updated timestamps

`radar.projection_batch_files`

- batch id + deterministic file ordinal/path
- source commit, blob SHA, content SHA-256
- status (`PENDING`, `PROJECTED`, `IDEMPOTENT`, `CONFLICT`, `FAILED`)
- provider result/evidence

Exact SQL names may change during implementation, but the state distinctions and transactional invariants may not be collapsed away.

### 6.3 Claims and overlap

`workflow_run` and schedule jobs can overlap. Lane claims therefore require provider-side atomic compare-and-set/lease semantics. GitHub Actions `concurrency` is advisory optimization only; cancellation must not be able to manufacture a false-complete cursor.

Expired claims can be recovered, but recovery must inspect durable batch/file state before resuming.

### 6.4 Ancestry decisions

Given durable projected cursor `C` and observed active-lane head `H`:

- `C == H`: `NOOP`.
- `C` is ancestor of `H`: validate/process the complete `C..H` history in order.
- `H` is ancestor of `C`: stale wake-up; `STALE_EVENT`, no rewind.
- neither is ancestor of the other: `DIVERGED_HISTORY`, fail closed, preserve evidence, do not advance.

Missing/deleted canonical branch: `CANONICAL_LANE_MISSING`, no retarget-by-name heuristic.

### 6.5 Bootstrap

Never seed `projected_head_sha` to a current branch head merely because the branch exists. The current outage proves provider coverage can lag Git.

New journal rows start `UNINITIALIZED`. First trusted reconciliation validates canonical history from the approved lineage/cutover anchor, replays Git-backed messages idempotently against provider state, and advances `projected_head_sha` only after every file through the target head is established as projected/idempotent with no unresolved conflict.

Full initial replay is permitted by design because Git remains canonical and projection is idempotent/collision-aware. Executing that replay against the live provider is a separately authorized provider effect.

## 7. Canonical message grammar and cross-runtime conformance

Python writer admission, Python projection, and TypeScript Edge parsing currently differ. A message can be admitted to immutable Git and later rejected or normalized differently.

Define one language-neutral `BUS_MESSAGE_GRAMMAR_V1` contract and a shared fixture corpus containing accepted and rejected byte-exact documents plus expected normalized fields.

At minimum the grammar must define:

- UTF-8 requirement;
- optional one-line Markdown title;
- YAML-style frontmatter boundaries and scalar-only handling;
- inline metadata block boundaries;
- duplicate header handling and key normalization;
- quote/backtick scalar unwrapping;
- required `message_id` and `writer` semantics;
- canonical writer/lane match and ID namespace rules;
- `requires_reply` and `requires_ack` accepted boolean lexemes;
- recipient tokenization/identity normalization;
- timestamp policy, including whether timezone-less non-date timestamps are invalid rather than silently assumed UTC;
- `#ENDTHREAD` body-terminal semantics;
- exact body/full-byte hashes.

Writer-lane admission must validate every field whose malformed value would make trusted projection fail. Edge and Python implementations must execute against the same fixture corpus in CI. Duplicate language implementations are acceptable only with this conformance oracle.

The original Radar middleware's deterministic duplicate key remains payload-only SHA-256 and the 500 ms semantic remains unchanged.

## 8. Body-bound GitHub OIDC

### 8.1 Request binding

For each HTTP projection request:

1. serialize the exact canonical JSON request body bytes once;
2. compute SHA-256 of those exact bytes;
3. request a fresh GitHub OIDC token with audience `chat-communication-bus-supabase:<body_sha256>`;
4. send the same digest in a dedicated request header;
5. send the exact serialized bytes used for the digest.

A fresh OIDC `jti` is required per chunk/request.

### 8.2 Edge verification order

Before parsing the request as trusted projection data, Edge must:

- verify GitHub JWT signature and temporal claims;
- verify repository identity;
- verify exact trusted reusable `job_workflow_ref` and `job_workflow_sha` for commit `A`;
- accept only the intended central caller event classes (`workflow_run` and `schedule`) and expected default-branch caller context;
- compute SHA-256 over the exact received body bytes;
- require the digest header and body-bound audience to match that hash;
- only then parse the batch and consume the one-time JTI;
- only then invoke provider projection RPCs.

The current branch-local assumptions (`event_name=push`, OIDC `ref=bus/...`, OIDC `sha=batch.branch_head`, branch caller workflow prefix) must be removed. Lane ref/head are trusted because the immutable reconciler derived and body-bound them, not because they equal the caller's standard OIDC ref/sha.

Replay protection is credential replay protection, not business idempotency. If a response is lost after commit, a retry uses a fresh JTI and safely replays the same Git-backed operation under provider message/content idempotency.

## 9. Radar Phase 2: durable node-level registry and routing

### 9.1 Data model

A subscription must identify the concrete node that is waiting for work, not only the logical identity. The durable schema/model must contain at least:

- `node_id` -> `identity_id` binding;
- node status;
- last heartbeat / lease expiry;
- node capabilities as applicable;
- subscription `node_id`, `domain`, optional `intent`, and `min_priority`;
- active/enabled state.

Identity-level subscriptions may exist as configuration templates, but runtime routing authority must resolve to node-level active subscriptions.

### 9.2 Lease semantics

A node is routable only when it has a valid heartbeat/lease. A routable status with `last_heartbeat IS NULL` is never considered live. `mark_stale_nodes_offline` must fail closed for invalid non-positive lease intervals and expire/null-heartbeat routable records according to explicit bootstrap semantics.

Startup registration/heartbeat and subscription reconciliation must be atomic enough that Radar does not route against a partially registered node.

### 9.3 Route result

Routing returns exact node recipients, with their owning identity available as metadata. It matches both domain and intent when an intent subscription is present, applies the priority threshold, and excludes expired/offline/paused/archived nodes.

`routed` telemetry must mean an actual route/delivery handoff defined by the runtime contract, not merely “an identity matched a subscription.” Separate counters may record matched, enqueued, dispatched, delivered/handed-off, dropped, and DLQ as needed.

## 10. Migration and recovery provenance repair

### 10.1 Restore already-applied migration identities

Rename Git source files to the exact provider ledger versions without changing their historical effect semantics:

- `20260902_radar_control_plane_v1.sql` -> `20260902120716_radar_control_plane_v1.sql`
- `20260902_radar_realtime_v1.sql` -> `20260902120826_radar_realtime_v1.sql`
- `20260902_radar_visual_identity_v1.sql` -> `20260902203610_radar_visual_identity_v1.sql`
- `20260902_radar_live_message_projection_v1.sql` -> `20260902204759_radar_live_message_projection_v1.sql`
- `20260902_radar_live_message_collision_v1.sql` -> `20260902231445_radar_live_message_collision_v1.sql`
- `20260902_radar_receipt_plane_v1.sql` -> `20260903000603_radar_receipt_plane_v1.sql`
- `20260903_radar_assignment_plane_v1.sql` -> `20260903001906_radar_assignment_plane_v1.sql`
- `20260903_radar_operator_views_v1.sql` -> `20260903113314_radar_operator_views_v1.sql`

### 10.2 Give unapplied migrations honest versions

Rename source-only files to unique, unapplied versions based on their first durable Git introduction:

- `20260903_radar_thread_closure_v1.sql` -> `20260903214334_radar_thread_closure_v1.sql`
- `20260905_radar_oidc_replay_guard_v1.sql` -> `20260905232637_radar_oidc_replay_guard_v1.sql`

Any new journal/node-lease hardening migration receives a new version later than these; it must not reuse a historical provider version.

### 10.3 Forward hardening, not retroactive provider fiction

Already-applied migration files should represent the historical source that produced provider state. Security/currentness corrections that would change live state—such as revoking inherited PUBLIC EXECUTE, fixing node lease behavior, changing publication membership, adding journal tables, or changing subscription shape—belong in new forward migrations.

Local rebuild fidelity is proved by applying the restored historical chain followed by the forward hardening migrations.

## 11. Database CI and recovery testing

Add a database CI job using:

- `supabase/setup-cli` pinned by immutable action commit SHA;
- an exact stable Supabase CLI version;
- a local Supabase stack;
- `supabase db reset` to prove the complete migration chain applies in timestamp order;
- execution of every Radar SQL assertion against the reset database.

Fix the ambiguous Realtime test expression. Make its expected publication set match the intentionally selected current contract. Add executable SQL coverage for thread closure, replay guard, journal/CAS behavior, node leases/subscriptions, function ACLs, and all later forward migrations.

Tests must prove client roles cannot obtain schema/table/view/sequence/function privileges beyond the documented surface. Public PostgREST bridge functions remain service-role-only.

Historical snapshot seed files remain historical. Current recovery must not replay an old writer-lane snapshot as current topology. Current self-registration/topology projection should be generated/read from canonical topology state or a clearly current idempotent seed contract.

## 12. Realtime contract

Production currently publishes `nodes`, `assignments`, `dependencies`, `acknowledgements`, `reconciliation_events`, `messages`, and `identity_visuals` from `radar`.

The source live-message migration deliberately added `messages` and conditionally `identity_visuals`. Unless a separate privacy/load decision changes that contract, documentation and SQL tests shall describe this actual intentional set rather than claiming messages are excluded.

If publication membership is changed later, that is a forward provider migration and separately reviewed operational decision.

## 13. Projection-trigger scaling

Current receipt and assignment triggers call full-corpus reconcilers after every message insert and serialize globally with advisory transaction locks. This is correct enough for current idempotency but amplifies retries and grows poorly with corpus size.

The source hardening shall add performance/regression tests and then move derived reconciliation toward incremental inserted-message work where semantic equivalence can be proven. It must preserve:

- projection event idempotency;
- reply-reference ambiguity handling;
- assignment fixed-point/predecessor correctness;
- append-only reconciliation evidence;
- transaction rollback on derived-effect failure.

If a safe incremental rewrite cannot be proven in the same implementation packet, retain the current functions and record the scaling issue as an explicit bounded follow-up rather than weakening correctness.

## 14. Legacy Slack relay

`chat_bus.slack_relay` is not the active transport and is not exported from the package root, but remains importable source code. Harden it under TDD rather than leaving race-prone behavior:

- explicit SQLite thread-sharing policy with timeout and lock;
- atomic/idempotent claim semantics under concurrent callers;
- correct distinction between operation-id and message-id conflicts after races;
- `mark_delivered` must reread durable state after conditional update and never return a caller timestamp that lost the race;
- no new Slack network dependency or credential ownership.

## 15. Supply-chain reproducibility and custody

### Python

Runtime dependencies are currently empty. Pin build/test tooling to exact versions (including build backend/test runner and any pip/tool bootstrap used in CI) through a reviewed constraints/lock mechanism. Remove unbounded `pip install --upgrade pip` behavior.

### Edge

Pin `@supabase/supabase-js` and the Supabase Edge runtime type import to exact versions. Add Deno lock/config or an equivalent deterministic dependency record and verify it in CI.

### Source custody

Replace the three-file `radar_source_hashes.py` allowlist with a manifest-driven custody check covering all provider-critical artifacts, at minimum:

- every Radar migration and SQL test;
- current seeds/currentness projection source;
- Edge handler/index/config and dependency lock;
- central dispatcher/trusted projector workflows;
- canonical parser grammar/fixtures;
- topology/onboarding/cutover contracts.

The custody check detects omitted critical files as well as hash drift.

## 16. Currentness/documentation repairs

After source behavior is implemented and verified, update the present-tense contracts without rewriting historical evidence:

- `RADAR_CURRENT.json`;
- `RADAR_SUPABASE_V1.md`;
- `RADAR_SELF_REGISTRATION_V1.json`;
- current Radar seed/current topology projection;
- README;
- `docs/operator/RECOVERY.md`;
- `docs/BRANCH_DISPOSITION.md`;
- Parallax onboarding contract/test;
- the Radar restore checkpoint or a successor checkpoint;
- issue #16 with source/live sequencing facts.

Historical cutover, phase reports, and dated lane snapshots remain historical artifacts and should be labeled/treated as such rather than silently rewritten into present-tense truth.

## 17. Implementation and release sequence

Source implementation should be split so immutable trust anchors exist before callers pin them.

1. Repair test/currentness foundations that do not depend on a trust SHA: migration filenames, grammar/fixtures, topology active-state semantics, SQL-test scaffolding, bounded relay/runtime fixes.
2. Implement and verify the reusable trusted reconciler/projector plus source-level journal/RPC contracts. Commit this as immutable trust commit `A`.
3. Add the default-branch dispatcher that pins reusable workflow `A` and tests that no writer-branch code is executed.
4. Update Edge source for body-bound OIDC and central caller claims, pin its dependencies, and prove conformance in source tests.
5. Prepare forward provider migrations in dependency order: ACL/lease/subscription/journal/replay requirements before any Edge source that calls those RPCs is deployed.
6. Update present-tense contracts/docs and run the complete Python + SQL + source-custody suite.
7. Open a review PR. Do not merge automatically.
8. After separate provider authorization: apply migrations first, verify readback, deploy Edge with GitHub-OIDC gateway configuration, verify trusted central reconciliation on a bounded canary/backlog replay, then observe scheduled backstop.
9. Only after live evidence confirms parity should issue #16 be closed and old lane-local projector workflows be treated as non-authoritative/deprecated.

## 18. Acceptance criteria

The source implementation is not complete until automated tests prove all of the following:

- unknown Radar domain/intent still enters DLQ;
- priority 0 behavior and 500 ms payload-hash dedupe remain compatible with the original middleware contract;
- only `ACTIVE` canonical lanes can be reconciled;
- Parallax cannot project while onboarding remains gated;
- central reconciliation succeeds without executing writer-branch code;
- stale wake-ups no-op, forward ancestry processes the full delta, and divergent history fails closed;
- overlapping schedule/workflow-run claims cannot double-advance a lane;
- partial file/chunk failure cannot advance `projected_head_sha` past unconfirmed work;
- uninitialized bootstrap cannot skip provider backlog;
- request body substitution invalidates OIDC audience/digest binding;
- reused JTI is rejected while a fresh-JTI idempotent business retry succeeds;
- Python admission, Python projection, and Edge parser agree on shared conformance fixtures;
- malformed booleans/timestamps cannot be accepted into Git and later rejected by projection;
- routing returns exact eligible node IDs and honors domain, intent, priority, status, and lease;
- routable/null-heartbeat and expired nodes cannot receive work;
- 60-second heartbeat remains `domain: system`, `intent: telemetry`, priority 4, with durable routed/dropped/DLQ accounting semantics explicitly defined;
- clean local database reset reproduces the migration chain in provider-ledger order;
- every Radar SQL assertion actually executes successfully after reset;
- anon/authenticated cannot call Radar provider bridges or obtain unintended object privileges;
- Realtime tests match the intentional publication contract;
- current recovery cannot seed obsolete v1 writer routes;
- source custody covers every provider-critical artifact;
- the Slack relay is race-safe or explicitly removed/deprecated under a reviewed compatibility decision;
- complete Python, database, dependency/custody, and workflow trust tests pass on the exact branch head.

## 19. Security/reliability invariants

The following are non-negotiable throughout implementation:

- Git message history remains canonical durable evidence; Supabase remains rebuildable operational projection.
- A Git branch name is not an identity credential.
- A branch-local workflow is not trusted control code.
- A successful writer guard is not proof of provider projection.
- A provider projection row is not proof that a recipient read or incorporated a message.
- No cursor advances on ambiguity, divergence, unresolved conflict, or unknown partial commit state.
- Currentness is read from explicit current contracts/provider readback, not inferred from dated historical snapshots.
- Protected effects remain operator-authorized effects even when source code for them is fully prepared and tested.
