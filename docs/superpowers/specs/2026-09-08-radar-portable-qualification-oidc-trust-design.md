# Radar portable qualification and GitHub OIDC trust-boundary design

Date: 2026-09-08
Status: DESIGN FOR REVIEW — NO IMPLEMENTATION AUTHORITY
Repository: `thebrazenbeard/chat-communication-bus`
Successor branch at design start: `radar/reproducible-ci-source-custody-v1-20260906`
Design-start head: `cb90032ac153a63bb71e54a12e382caf10d064bf`
Design-start tree: `1e06c6d4e59c0640f377e2adde701895f952025b`

## Purpose

This design separates two problems that currently share symptoms but not root causes:

1. Radar qualification must prove an exact source cut without depending on paid/private hosted CI or on Windows PowerShell as a security primitive.
2. GitHub Actions projection requests must reach Radar's GitHub-OIDC verifier without being rejected first by Supabase's built-in user-JWT gateway, while remaining cryptographically and operationally fail-closed.

The goal is to reduce accidental coupling. GitHub remains canonical custody. Radar owns authorization/routing semantics. Supabase remains a rebuildable projection/runtime. Qualification proves an exact candidate cut. No layer silently substitutes its trust model for another layer's.

## Non-goals and protected effects

This design does not authorize:

- merge or rebase into `main`;
- provider migration application;
- Edge deployment;
- changing live `verify_jwt`;
- configuring `RADAR_TRUSTED_PROJECTOR_SHA`;
- cursor seed/bootstrap or reconciliation against the live provider;
- dispatcher activation;
- billing/account/payment changes;
- credentials/ruleset changes;
- branch-history rewrite.

Source implementation may prepare those effects, but live activation remains separately Patrick-authorized.

## Design principles

### One trust question per layer

- Git/GitHub answers: what exact source bytes and history are canonical?
- Qualification answers: did the required verification stages pass on this exact clean commit/tree?
- GitHub OIDC answers: which immutable GitHub workflow identity is calling?
- Radar Edge authorization answers: is that authenticated workflow allowed to request this exact operation/body?
- Projection journal answers: is this exact lane/batch/path claim still current and fenced?
- Supabase stores projection/runtime state; it does not become canonical custody.

### Authentication is not authorization

A cryptographically valid GitHub OIDC token is insufficient by itself. Radar must additionally require the expected repository, reusable workflow, branch/ref, request audience/body binding, replay state, and trusted immutable projector cut before privileged RPCs are reachable.

### Qualification semantics are platform-neutral

PowerShell may remain a Windows launcher, but the meaning of PASS must be defined by a machine-readable contract and a portable orchestration engine, not by shell choice.

## Part A — portable qualification engine

### Proposed source surfaces

- New canonical orchestrator: `scripts/radar_qualify.py`
- Existing `scripts/radar_local_qualify.ps1` becomes a thin Windows launcher that invokes the Python orchestrator.
- Existing `scripts/radar_validate_qualification_receipt.py` remains the admission validator.
- `RADAR_QUALIFICATION_V1.json` advances only as needed to describe portable execution and stage evidence.

### Orchestrator responsibilities

The Python orchestrator owns all qualification semantics currently embedded in PowerShell:

1. Resolve Git top-level and bind exact `HEAD` commit/tree.
2. Refuse a dirty checkout before execution.
3. Validate required tool versions:
   - Python 3.11 and 3.12;
   - pip 26.2.1;
   - Deno 2.9.6;
   - Supabase CLI 2.116.0;
   - Docker available/healthy;
   - `psql` available.
4. Run both Python environments using isolated temporary venvs.
5. Run compileall, full pytest, and `radar_source_hashes.py` under each required Python version.
6. Run `deno ci` and `deno check index.ts` in the Edge function directory.
7. Preserve the existing destructive-local-Supabase safeguards before `supabase start`.
8. Run `supabase start`, `supabase db reset`, every `supabase/tests/radar_*.sql` with `ON_ERROR_STOP=1`, and unconditional owned-resource cleanup.
9. Preserve primary SQL failure and cleanup failure independently.
10. Re-read commit/tree/full working-tree state after all stages and fail closed on drift.
11. Emit an external PASS receipt only after all required stages and cleanup succeed.

The PowerShell wrapper may only locate an appropriate Python interpreter and forward arguments. It must not own additional qualification semantics that do not exist in the Python engine.

### Platform policy

The initial portable engine supports Windows first because that is the currently documented operator environment. The implementation must avoid Windows-only path/process assumptions where practical so Linux/macOS execution can be qualified later without changing PASS semantics.

A new platform is not automatically authoritative merely because the Python engine can run there. `RADAR_QUALIFICATION_V1.json` must explicitly list authoritative platform profiles. This prevents accidental expansion of the trust surface.

## Part B — stage-evidentiary qualification receipts

### Receipt schema evolution

Advance the receipt schema rather than overloading schema version 1.

Each required stage records at least:

- stage identifier;
- start timestamp UTC;
- completion timestamp UTC;
- exit status;
- executable/version identity where applicable;
- SHA-256 of captured stdout;
- SHA-256 of captured stderr;
- deterministic ordinal in the required-stage sequence.

The final receipt records:

- schema version;
- status `PASS`;
- qualification mode/profile;
- source commit;
- source tree;
- working tree `CLEAN`;
- exact required toolchain;
- ordered stage records;
- SHA-256 over a canonical serialization of the ordered stage-evidence list;
- completion timestamp UTC.

This is forensic integrity, not independent cryptographic attestation. The receipt does not claim that an attacker who controls the qualification machine cannot fabricate evidence.

### Receipt location

The existing rule remains mandatory: receipt output must resolve outside the source checkout, even if an in-repo location is Git-ignored. Admission independently rechecks this path boundary.

### Admission

`radar_validate_qualification_receipt.py` must validate:

- schema/profile/status;
- exact toolchain;
- exact required stage set and order;
- each stage has terminal success evidence;
- overall stage-evidence digest matches canonical stage serialization;
- UTC timestamps are well formed and ordered;
- receipt path is external to checkout;
- checkout is still clean;
- receipt commit/tree equal current HEAD/tree.

Successful admission still performs no promotion, merge, anchor freeze, or live effect.

## Part C — GitHub OIDC Edge trust boundary

### Gateway configuration model

For `github-bus-ingest`, source configuration should declare `verify_jwt = false` because the caller presents a GitHub-issued OIDC bearer token, not a Supabase user JWT.

This does not make projection authorization anonymous. It moves authentication from the incompatible Supabase user-JWT pre-handler gate into the handler that understands GitHub OIDC. Privileged RPC creation must occur only after that handler finishes authentication and authorization.

The source change to `verify_jwt = false` is preparation only. Applying that configuration to the hosted provider is a separately protected effect.

### Required GitHub OIDC checks

The handler must fail closed unless all applicable checks succeed:

1. JWT shape and JOSE algorithm are supported (`RS256` for current GitHub OIDC source).
2. Signature validates against GitHub's OIDC JWKS.
3. `iss` exactly equals `https://token.actions.githubusercontent.com`.
4. `aud` exactly includes the body-bound Radar audience for the request.
5. `exp`, `nbf`, and `iat` satisfy existing freshness constraints.
6. `jti` exists and is accepted exactly once by the replay guard.
7. Repository name equals `thebrazenbeard/chat-communication-bus`.
8. Immutable `repository_id` equals `1324505476`.
9. Repository owner identity is cross-checked with immutable owner ID `234958733` where present/required by the selected claim policy.
10. Caller `workflow_ref` is the canonical dispatcher on `refs/heads/main`.
11. Caller `ref` is `refs/heads/main`.
12. `job_workflow_ref` points to the exact reusable trusted-projector workflow at the expected immutable projector SHA.
13. `job_workflow_sha` equals the expected trusted projector SHA.
14. Event type is explicitly allow-listed; no implicit event acceptance.
15. The request body's expected audience/hash binding is validated before any privileged projection mutation.

Mutable names are retained for readability and defense in depth, but immutable repository/owner IDs become mandatory identity axes so namespace changes cannot silently broaden trust.

### Subject claim

The handler must not rely on `sub` alone for authorization. GitHub now supports immutable subject formats and subject customization, but changing repository OIDC subject configuration is itself a GitHub repository setting/protected effect. Source tests may prepare support for an immutable-subject policy; enabling that policy requires separate authorization and a fresh observed token/claim fixture.

### Failure ordering

The intended request order is:

1. size/method/basic shape gates that require no secret or provider mutation;
2. parse authorization token;
3. verify GitHub signature/issuer/audience/time;
4. verify immutable and mutable caller identity claims;
5. initialize privileged Supabase client only after caller trust is established where implementation structure permits;
6. consume replay `jti`;
7. validate body-bound audience/hash and operation semantics;
8. execute claim-fenced atomic SQL projection.

No service-role projection RPC may be reachable on an unauthenticated/unauthorized path.

## Part D — adversarial test matrix

### OIDC negative cases

Tests must reject at least:

- wrong issuer;
- wrong audience;
- malformed/unsupported algorithm;
- unknown key or invalid signature;
- expired token;
- future `nbf`;
- stale/future `iat`;
- missing `jti`;
- replayed `jti`;
- correct repository name but wrong immutable `repository_id`;
- correct repository ID but wrong repository name;
- wrong owner ID;
- correct repository but wrong caller workflow;
- correct caller workflow but wrong ref;
- correct caller/ref but wrong reusable workflow;
- correct reusable-workflow path but wrong immutable workflow SHA;
- valid token for disallowed event;
- valid token with request-body/audience mismatch;
- valid token with stale projection batch claim;
- valid token with wrong claimed file path;
- valid token after control/topology cut changed.

### Gateway/config regression

Source tests must bind `supabase/config.toml` so the GitHub ingest function's intended source configuration is `verify_jwt = false`, and must state that this is source-only until provider deployment is separately authorized.

### Qualification negative cases

Tests must reject:

- missing stage;
- duplicated stage;
- reordered stage;
- nonzero stage exit;
- stage evidence digest mismatch;
- toolchain drift;
- commit/tree drift;
- dirty checkout;
- in-checkout receipt including ignored paths;
- malformed timestamps;
- receipt from a platform/profile not declared authoritative.

## Part E — staged implementation order

1. Add source tests for the portable qualification contract and preserve current PowerShell behavior as the compatibility baseline.
2. Introduce `radar_qualify.py` with no receipt-schema change first; make PowerShell a wrapper only after parity tests prove equivalence.
3. Add receipt schema v2 stage evidence and update admission tests.
4. Add immutable GitHub repository/owner claim checks and adversarial handler tests while live configuration remains untouched.
5. Add source config/test for `verify_jwt = false` and explicitly mark provider state as not applied.
6. Run the complete authoritative local qualification against one exact final successor commit/tree.
7. Admit its external receipt against that same clean checkout.
8. Only after PASS/admission, freeze a successor projector anchor in source.
9. Prepare a separate protected-effect recovery packet for Patrick covering provider migrations, Edge deployment/config, trusted SHA, cursor bootstrap, dispatcher activation, and end-to-end verification.

Any source repair after qualification invalidates the receipt and requires a complete rerun before successor-anchor freeze.

## 3DG3 challenge checklist

3DG3 (or any adversarial reviewer) should attack the design using these questions:

- Which invariant is protected by each layer, and is any invariant duplicated without benefit?
- Can a valid GitHub token from the wrong workflow/repository/ref reach a privileged RPC?
- Can a mutable GitHub name satisfy trust without its immutable ID agreeing?
- Can the replay guard mutate before enough identity claims are checked?
- Can body parsing or audience derivation differ between the workflow and Edge handler?
- Can an expired/stale projection claim mutate provider state before journal fencing?
- Can qualification PASS if any required stage was skipped, repeated, reordered, or only partially executed?
- Can the qualification wrapper and portable engine disagree about semantics?
- Can an old receipt be admitted after source/config/toolchain change?
- Can any source-only setting be mistaken for a deployed/provider fact?
- Is `verify_jwt = false` ever described as equivalent to anonymous authorization rather than merely disabling the incompatible Supabase user-JWT pre-gate?
- Is there any simpler architecture that preserves the same invariants with fewer trust roots?

## Acceptance criteria

The source design is ready for implementation only when Patrick accepts this spec.

Implementation is ready to become a successor candidate only when all source tests are green and currentness/custody contracts agree.

The successor candidate is ready for anchor freeze only when the exact authoritative no-paid qualification completes and the resulting external receipt is admitted against the same clean commit/tree.

Live recovery is ready only after a separately authorized provider packet succeeds end to end; source readiness alone never proves provider recovery.
