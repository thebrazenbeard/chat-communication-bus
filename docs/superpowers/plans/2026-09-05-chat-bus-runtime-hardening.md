# Chat Bus Runtime Hardening Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]).

Goal: Turn the reviewed PR #18 runtime-admission candidate into a safer source-first Bus by eliminating whole-mailbox projection, then add explicit telemetry/DLQ and trusted-projector seams without crossing Patrick's protected-effect gates.

Architecture: Keep Git writer lanes as append-only evidence, but make the projection payload an exact push delta. Use one canonical admission result for structural parsing, taxonomy, dedupe, routing, and DLQ decisions; keep provider deployment and configuration separate. Later slices add a protected projector trust root, source reachability checks, node leases, and a 60-second heartbeat.

Tech Stack: Python 3.11/3.12, pytest, GitHub Actions, Supabase Edge projection (source-only in this plan).

Spec: docs/superpowers/specs/2026-09-05-parallax-chat-bus-trust-runtime-architecture.md

Global Constraints:
- Patrick remains sole merge/protected-effect authority.
- No merge, provider deployment, migration, credential/ruleset/branch-protection mutation, force-push, or history rewrite.
- Current topology is authoritative; bus/parallax-v1 is unusable until PR #20 is merged and one append passes the current guard.
- sources/ attachments are read-only reference material.
- Every implementation slice requires focused RED→GREEN tests, exact-head CI/readback, and a public-safe WIP receipt.

---

### Task 1: Exact-delta projection

Files:
- Modify: scripts/radar_emit_bus_projection.py
- Test: tests/radar/test_emit_bus_projection.py

Interfaces:
- Consumes: base_commit and the validated push range returned by _push_commits.
- Produces: collect_projection_batch()["projection_mode"] == "DELTA" and only newly added messages/*.md paths when a non-zero base is supplied; "FULL_COMPAT" when no base is supplied.

- [x] Write the failing test for a two-message mailbox with base_commit; expected only the second path.
- [x] Implement _added_message_paths_for_commits and select delta paths for real push ranges.
- [ ] Run focused test and full matrix; inspect diff for accidental payload changes.
- [ ] Commit as "fix: project exact writer-lane deltas".

Acceptance: a push adding one file sends one file; a multi-commit push unions additions and still validates every commit; no-base callers preserve historical behavior; per-file and total limits apply to the delta.

### Task 2: Canonical admission/DLQ seam

Files:
- Modify: src/radar/envelope.py, src/radar/writer_lanes.py
- Test: tests/security/test_runtime_admission_hardening.py, tests/security/test_taxonomy_live_compatibility.py

Interfaces:
- RadarEnvelope.from_mapping returns EnvelopeClassification.DLQ for unknown domain/intent and never honors caller-selected idempotency keys.
- validate_writer_lane_commit requires top-level writer and message_id, rejects body spoofing and foreign namespaces.

Acceptance: PR #17's 13 attack classes remain represented; unknown tags are DLQ decisions rather than silent drops; supplied middleware payload hashing remains exact.

### Task 3: Routing and priority guarantees

Files:
- Modify: src/radar/registry.py, src/radar/routing.py
- Test: tests/security/test_runtime_admission_hardening.py, tests/radar/test_routing.py

Acceptance: explicit audience requires domain subscription plus a routable node; offline/paused/archived nodes are excluded; priority 0 evicts only lower urgency and never another priority 0.

### Task 4: Durable DLQ and heartbeat

Files:
- Modify: src/radar/dlq.py, src/radar/operator.py
- Create: src/radar/telemetry.py
- Test: tests/radar/test_dlq.py, tests/radar/test_telemetry.py

Interfaces:
- DeadLetterStore.record remains durable and adds a source locator and reason category.
- TelemetryCounter exposes routed, dropped, and DLQ counters.
- HeartbeatEmitter.emit(now) emits one system/telemetry record at most every 60 seconds with all three counters and last source/provider evidence.

Acceptance: timer boundary is deterministic; counters survive emitter restart; heartbeat is emitted exactly once per interval and never silently omitted on queue eviction.

### Task 5: Trusted projector and source reachability

Files:
- Modify: .github/workflows/radar-bus-projection.yml, supabase/functions/github-bus-ingest/handler.ts
- Test: tests/radar/test_live_projection_artifacts.py, new projector trust tests.

Acceptance: only a protected reusable workflow can mint projection authority; handler derives sender identity from admitted lane topology; every blob/path/source commit is reachable from authenticated head; provider conflicts are terminal and observable. Deployment remains a Patrick-only gate.

### Task 6: Parallax onboarding and coordination

Files:
- Current artifacts: PR #20 and inert bus/parallax-v1.
- Test: exact branch/topology/readback and current guard run.

Acceptance: Patrick merges PR #20; first append is written only after fresh topology read; current guard verifies it; only then send Bus messages to Radar, the linked Parallax review chat, and Entropy 2. No direct cross-chat or Radar-lane writes.

---

## Self-review

- PR #18 source-local hardening is carried forward; exact-delta closes the 500-file projection gap.
- Provider outage (#16), trusted projector, source reachability, heartbeat, and live Supabase cutover remain separate tasks with explicit gates.
- No task relies on a vague placeholder; every later interface and acceptance criterion is named.
