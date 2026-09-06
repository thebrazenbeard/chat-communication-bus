# Radar restore checkpoint — 2026-09-06

Status: source hardening substantially implemented; provider/runtime qualification still blocked.

Fresh-read GitHub and provider before acting. This checkpoint is continuation evidence, not authority to merge, migrate, deploy, seed cursors, change Edge auth/configuration, mutate billing/credentials/settings/rulesets, or rewrite history.

## Current source stack

Canonical `main` observed during this work: `87df9b1372d0f65b5c3ced0296122b2140084024`.

PRs #33 and #34 were externally merged into their stacked feature bases, not into canonical `main`.

Open Draft source PR stack:

- PR #35 — reproducible CI/source custody. Exact Python/Supabase/Deno tool pins and SQL-CI source.
- PR #36 — currentness/recovery closeout. Current Radar mailbox is `bus/radar-v2`; provider is explicitly partial/not current; recovery seed is node-bound and deliberately OFFLINE/lease-less.
- PR #38 — immutable projection anchor C: `f5ab21244a111b47708fa11e99d0e8ff7d8f5a45`, tree `a7dd785be8dfea883df052a73378d583e53058d1`.
- PR #37 — source-only successor to anchor C. Dispatcher, `RADAR_PROJECTION_TRUST_ANCHOR_V2.json`, and `RADAR_CURRENT.json` bind C exactly; B is historical only. This successor also contains the genuine Deno 2.9.6-generated Edge lockfile.

The branch head before this checkpoint refresh was `939b89df3444f7db90eec29938e6ff77f608d856`. Fresh-read after restore because this checkpoint update advances the branch again.

## Anchor C trust model

Anchor C fixes a hostile-review defect in B: B froze topology bytes together with immutable projector code, so later reviewed `main` topology changes would have been invisible.

C keeps executable code immutable while checking out current `main` separately as credential-less inert Git data. Only `control/src` and `control/scripts` execute. Current-main topology/cutover bytes are read as data and their Git object evidence is journal-fenced. Writer-lane code is never executed.

## Hostile invariants reviewed at source level

Source inspection on the stacked C successor establishes the intended implementations for:

1. no writer-branch or mutable-main code execution by the trusted projector;
2. no cursor advance after stale/lost projection claim or unresolved file result;
3. canonical Bus grammar applied during writer admission before immutable append acceptance;
4. routing returns exact authorized live node IDs rather than identity-only recipients;
5. exact-body GitHub OIDC binding and JTI consumption before semantic JSON parsing;
6. unique, provider-ordered Radar migration timestamps across the 13-file source chain.

These are source-review findings, not a substitute for executable qualification.

## Reproducible Deno lock provenance

The prior missing-lock gate is closed at the source-artifact level without hand-authoring the lock.

Private hosted runners were unavailable, so public `thebrazenbeard/wip` was used only as non-secret dependency-resolution compute. No private Bus source, messages, credentials, or provider data were copied there.

WIP helper evidence:

- branch: `radar/deno-lock-generator-v1-20260906`;
- pinned dependency config identical to `supabase/functions/github-bus-ingest/deno.json`;
- Deno: exactly `2.9.6`;
- generation: `deno install --entrypoint deps.ts --frozen=false`;
- verification: `deno ci` then `deno check deps.ts`;
- successful generation run: `34053270798`, job `101540559482`;
- successful artifact-producing run: `34053386984`;
- artifact ID: `9995230697`;
- artifact ZIP SHA-256: `ad095737a9d0aea5fb36630aec7c80662b83e988f54a85ea43884713ebe24a3b`;
- extracted `deno.lock`: 9,967 bytes, SHA-256 `ef49fc6e098fa0ca6392b5beaa40a9787fd66800823eee8c45e17f1eae553683`;
- exact Git blob SHA: `7fe9650c1ea2258877f55e254d3835cc0927c667`.

The exact artifact bytes were imported as a base64 Git blob, independently recomputed to the same Git blob SHA, and committed to the PR #37 successor at `939b89df3444f7db90eec29938e6ff77f608d856` as `supabase/functions/github-bus-ingest/deno.lock`.

This proves lock generation/byte custody for the pinned dependency stub. It does not substitute for running the private repository's complete Edge/Python/SQL CI on the integrated source tree.

## Verification blocker — issue #39

Issue #39 owns the separate Actions verification-infrastructure incident.

The blocker is now narrowed beyond a generic GitHub outage:

- private `chat-communication-bus` CI repeatedly creates jobs that fail in about two seconds with `steps: []`, `runner_id: 0`, and no logs;
- private `vera-control-plane` run `34043844584`, attempt 3, job `101534728901` reproduced the same zero-step/zero-runner signature;
- after GitHub public status reported Actions operational, an explicit Chat Bus rerun still failed before runner assignment;
- a same-time rerun in public `thebrazenbeard/wip` immediately received a real standard hosted runner (`runner_id: 1000005165`), establishing that hosted runners work for the account's public repository while private repositories are blocked.

This is strongly consistent with a private-repository Actions metering/entitlement gate, but the exact account condition remains UNKNOWN because connected APIs do not expose the private check annotation text or account billing/budget/payment state. Do not infer or change billing/settings without direct account evidence and Patrick authorization.

Fresh exact-head CI after the generated lock commit: run `34053580968` on `939b89df3444f7db90eec29938e6ff77f608d856`. Python 3.11, Python 3.12, Edge, and SQL all again completed with zero steps and `runner_id: 0`, so no repository code executed.

Until the complete Python/SQL/Edge suite executes successfully, do not label the stack GREEN or runtime-qualified.

## Provider incident / current readback

Issue #16 remains OPEN.

Fresh 2026-09-06 readback:

- provider Radar migration ledger stops at `20260903113314_radar_operator_views_v1`;
- five later Git-held Radar migrations remain unapplied;
- projection journal/replay-guard objects required by the new source are absent;
- `github-bus-ingest` remains ACTIVE v3 with `verify_jwt=true`;
- anchor C is not deployed/configured;
- projection cursors are not seeded;
- body-bound central OIDC source is not live.

No provider write/effect was performed during this source work.

## Bus coordination state

Radar lane `bus/radar-v2` contains:

- `radar-0062` at commit `39a6e40a5a31e196f88ac23809c55e61e1e0c988`, recording the source hardening boundary;
- `radar-0063` at commit `8b63f3673b81e1947b0bf9b2484c0d8e989fa0fd`, recording the cross-private-repository CI blocker diagnosis.

Their push-time Writer Lane Guard cannot currently provide executable admission evidence because private hosted-runner assignment is blocked by issue #39. Their Git append structure was separately read back and verified.

## Restore / continuation

On restore:

1. fresh-read `main`, PRs #35-#38, and their exact heads;
2. fresh-read issues #16 and #39 plus provider migration/Edge state;
3. inspect the exact private-job UI annotation and Actions billing/usage/budget/payment state before changing any account setting;
4. once private hosted runners are available, execute the full Python 3.11/3.12 + SQL reset/assertions + Edge frozen-lock CI on the exact candidate head;
5. rerun the hostile invariant suite on the exact candidate;
6. keep status `SOURCE IMPLEMENTED / EXECUTABLE QUALIFICATION BLOCKED / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN` until executable/provider evidence changes it;
7. do not merge/deploy/apply protected effects without separate Patrick authorization.

Recommended restore command:

`RADAR::RESTORE::CHAT_BUS_HARDENING_2026-09-06 — Read docs/checkpoints/RADAR_RESTORE_2026-09-06.md from the current source stack, fresh-read main, PRs #35-#38, exact-head CI, issues #16/#39, and provider state, then continue from the private-runner/provider boundary. Do not invent GREEN evidence and do not merge/deploy/apply protected effects without my explicit authorization.`
