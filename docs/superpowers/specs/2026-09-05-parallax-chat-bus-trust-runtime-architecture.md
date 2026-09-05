# Parallax Chat Bus trust-runtime architecture review

Status: DESIGN PROPOSAL — no production implementation or protected effect
Author: Parallax
Date: 2026-09-05

## Decision summary

The Chat Communication Bus currently behaves as a Git-backed coordination journal plus an asynchronous Supabase projection. It is not yet a continuously available message bus. The safest next architecture is a staged hybrid:

1. Git writer lanes remain append-only source evidence and human-readable recovery history.
2. A protected, reusable projector authenticates the workflow root and derives sender identity from the admitted lane/ref; message bytes cannot select identity.
3. Projection becomes exact-delta and idempotent, with durable quarantine/DLQ records for rejected or unprojectable files.
4. A persistent reconciler owns node leases, subscriptions, routing authorization, priority queues, scoped dedupe, heartbeat telemetry, and replay.
5. The operator cockpit reads those durable state surfaces; it does not invent state from branch names or missing provider rows.

This proposal deliberately does not recommend making Supabase the sole source of truth, raising the Edge file ceiling, or merging the existing hardening PRs independently.

## Verified current facts

The following were checked against the current repository/provider state during this review:

- Chat Bus `main` is `b2950bcb547fb78d16e44cd94a6ba2164937bf44`.
- PR #15 is open/draft at `c3c4172a685851a8cf032cb57770965a918c469a`; its CI is green, but the appender is not installed as the operating write path.
- PR #17 is open/draft and intentionally RED at `8236bb41db8f17e06b69ef943c6d2725a417749b`; both supported Python matrices reproduce 13 failures while the normal suite passes.
- PR #18 is open/draft at `5c1ea988d22357728ed3f9eeb08561edf100a9bc`; both matrices report 196/196 passing, but its Router/PriorityQueue/DedupeWindow/IdentityRegistry are not on the live writer-push → full-mailbox emitter → Edge path.
- Issue #16 is open. Supabase `github-bus-ingest` is active v3 with `verify_jwt=true`; the GitHub Actions OIDC bearer receives HTTP 401 at the gateway before the custom verifier. No redeploy was performed.
- Read-only provider state contained 216 projected messages, zero DLQ rows, no nodes, and no telemetry rows at review time.
- `bus/radar-v2` contains a later forbidden root `sbtest` commit; the guard detected it after the write, proving detection is not prevention and that full-history validation can grandfather an invalid ancestor.
- The emitter projects a whole mailbox and therefore meets an Edge 500-file ceiling before the system has a principled delta/replay boundary.
- The current strict taxonomy requirement is not yet represented by a durable DLQ/heartbeat operating surface.
- `radar_middleware_draft.py` defines payload-only SHA-256 deterministic hashing. Used as a global dedupe key, that collides unrelated routes with equal payloads; the key needs route/context scoping while preserving deterministic payload hashing as an input component.

These facts are not historical claims from Radar; they are the review cut used for this proposal.

## Findings

### BUG

1. Provider admission is incompatible with the deployed authentication design: Supabase gateway JWT verification rejects GitHub Actions OIDC before the Edge handler can verify it.
2. A writer-controlled workflow can currently be the authority that presents OIDC to the projector. The workflow root is therefore mutable at the same trust boundary it is supposed to establish.
3. Sender identity can be selected by message-controlled `writer:` bytes instead of being derived from an authenticated lane/ref.
4. Full-mailbox projection has a hard file-count failure mode and no durable exact-delta cursor.
5. Provider `CONFLICT` and projection failure have historically been able to look successful at the emitter boundary; PR #18 fixes one conflict case but the contract still needs durable delivery outcomes.
6. The specified 60-second system/telemetry heartbeat with routed/dropped/DLQ counts is absent.
7. Priority-0 admission, subscriptions, node state, taxonomy, and dedupe are currently implemented in helpers/tests that the live emitter path does not invoke.
8. Writer-lane guard validation occurs after a Git push; it can reject delivery without preventing the bad Git write, and a later valid-looking head may inherit a forbidden ancestor unless the base is checked correctly.

### DESIGN_DEBT

- Three parsers disagree: PR #15 safe appender, PR #18 writer parser, and Edge parsing. A message can be accepted by one and rejected by another.
- A branch is simultaneously treated as provenance, mailbox, identity credential, and deployment trigger. Those roles should be explicit interfaces.
- The current topology/cutover contract is a static snapshot, while node liveness and authorization are dynamic facts.
- Payload-only dedupe is deterministic but semantically over-broad.
- “No provider row” is overloaded as no message, projection outage, rejected message, and unobserved message.
- The system has no single delivery state machine spanning Git observation, admission, routing, provider persistence, and recipient acknowledgement.

### MISSING_CAPABILITY

- Durable append admission with compare-and-swap or a central append service.
- Reconciliation cursor per lane and per projector version.
- A first-class DLQ/quarantine record retaining reason, source locator, immutable commit, and retry policy.
- Leased node registration with expiry and explicit routable states.
- Recipient delivery/ack/read state independent of source message existence.
- Heartbeat scheduler that emits routed/dropped/DLQ counters every 60 seconds.
- Replay from Git evidence into provider state without re-reading an entire mailbox.
- Cross-worker discovery/wakeup that does not require polling every branch.
- Machine-readable authority/evidence separation.

### SIMPLIFICATION

- Keep Git as source evidence, but stop treating every lane commit as an application-level transaction. One commit may contain one or many files; the projector should consume immutable file identities and a monotonic cursor.
- Use one canonical parser library for Markdown/frontmatter and share its fixture corpus with the Edge implementation.
- Make topology a declarative binding/alias document; keep liveness, subscriptions, queue occupancy, and delivery state in the runtime database.
- Replace a broad “all helpers are the bus” model with a small explicit state machine and adapters.

## Approaches considered

### A. Patch the current workflow and full-mailbox emitter

Pros: smallest diff; preserves today’s operational shape.

Cons: does not remove workflow-root trust, sender spoofing, whole-mailbox scaling, or absence of durable delivery state. This is acceptable only as containment while B is built.

### B. Protected hybrid journal + reconciler (recommended)

Git remains durable source evidence and recovery history. A protected reusable workflow emits exact deltas to a projector whose identity is derived from the authenticated lane/ref. A runtime reconciler owns liveness, routing, priority, dedupe, DLQ, heartbeats, replay, and acknowledgements.

Pros: preserves auditability and offline recovery while giving the system real runtime semantics; each trust boundary has one owner; migration can be staged.

Cons: two storage planes and a reconciliation cursor must be operated; Git delivery remains eventually consistent.

### C. Provider-first broker with Git as archive

A managed queue/event stream is the sole live transport; Git receives signed archival receipts.

Pros: better latency and scaling.

Cons: requires new protected infrastructure and changes the communication contract; weakens “what was authored” visibility during outage; not justified until current semantics are correct.

## Target contract

### Identity

`lane_ref + authenticated_workflow_identity + commit_sha` identifies the source. The message header's `writer:` is metadata checked against, never used to select, the identity.

### Admission

The canonical parser validates UTF-8, frontmatter/header shape, required IDs, identity namespace, strict domain/intent taxonomy, and append-only path rules. Unknown tags become durable DLQ records, not silent drops.

### Projection

A protected projector accepts only exact deltas from a trusted reusable workflow. It records `observed → admitted/rejected → projected/conflicted/failed` per source file. Retries are idempotent by immutable source locator plus content hash.

### Routing

A reconciler computes authorized recipients from current topology, active node lease, and subscription. `audience` is a request, not authority. Offline/expired nodes cannot receive ordinary traffic. Priority 0 has reserved capacity and cannot be evicted by background traffic.

### Delivery

Each recipient gets a durable state: `QUEUED, SENT, ACKED, READ, EXPIRED, DLQ`. Source existence, provider persistence, and recipient acknowledgement are separate facts.

### Observability

Every 60 seconds, a heartbeat row/event records system status plus routed, dropped, DLQ, conflict, and projection-failure counts, with a monotonic interval ID. Missing heartbeats are themselves an alertable state.

## Migration and dependencies

1. Contain issue #16 without weakening the gateway globally; reconcile the exact deployed source and obtain Patrick's explicit provider-effect authorization before any redeploy.
2. Keep PR #17 as the adversarial oracle, but correct its taxonomy expectation from “reject” to “DLQ” and split live-path tests from helper tests.
3. Do not merge PR #15 or #18 independently. Consolidate one canonical parser/admission module and wire it into the actual guard/emitter path first.
4. Add trusted reusable-workflow binding, lane-derived sender, exact-delta cursor, and durable projection outcomes.
5. Add node leases/subscriptions/routing and priority queues in the reconciler.
6. Add scoped deterministic dedupe: `sha256(canonical_payload)` remains required, but the dedupe key is `hash(route_context || canonical_payload)` with the route context explicit.
7. Add heartbeat and DLQ before building a cockpit.
8. Onboard Parallax only after the topology PR is merged and one append passes the current guard; then coordinate with Radar, Entropy 2, and other active Work chats through this lane.

## Acceptance criteria

- A forged workflow from a writer lane cannot authenticate as the projector root.
- A message cannot change its sender by editing `writer:`.
- A projection retry processes only new/changed source files and is idempotent.
- Every unknown taxonomy tag creates a DLQ row with immutable source locator and reason.
- Priority-0 traffic is admitted under background saturation, with any eviction counted.
- An offline/expired node is not an authorized recipient.
- Two equal payloads on different routes do not dedupe each other; equal payload and equal route context within 500 ms does.
- A heartbeat appears every 60 seconds with routed/dropped/DLQ counts; a missing interval is detectable.
- A provider conflict or auth failure is visible as non-success at every caller boundary.
- A replay from Git reconstructs provider state without duplicating accepted messages.

## Authority boundaries

Patrick alone may merge PRs, change branch protections/rulesets, deploy or migrate Supabase, alter provider configuration, change credentials, or activate protected infrastructure. Parallax may create isolated branches, tests, design records, and Draft PRs. Radar owns operational integration after topology activation. Entropy 2 may execute only an approved bounded implementation packet. No worker may use Parallax's lane for coordination until the onboarding gate is verified.

## Decision gate

This document is a design review artifact, not implementation authorization. The next implementation action is to convert the accepted sections into a bounded task plan, then execute test-first on an isolated branch with PR #17 as the red-team acceptance oracle.
