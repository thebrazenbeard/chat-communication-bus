# Radar restore checkpoint — 2026-09-06

Status: source hardening substantially implemented; provider/runtime qualification still blocked.

Fresh-read GitHub and provider before acting. This checkpoint is continuation evidence, not authority to merge, migrate, deploy, seed cursors, change Edge auth/configuration, mutate credentials/settings/rulesets, or rewrite history.

## Current source stack

Canonical `main` observed during this work: `87df9b1372d0f65b5c3ced0296122b2140084024`.

Open Draft source PR stack:

- PR #33 — body-bound OIDC + durable central projection source. Frozen projection anchor B: `7076c73595d5a572e0f374c3a495b29982d92bed`.
- PR #34 — successor that originally repointed dispatcher to B.
- PR #35 — reproducible CI/source custody. Exact Python/Supabase/Deno tool pins and SQL-CI source are present; a genuine Deno-generated `supabase/functions/github-bus-ingest/deno.lock` is still absent.
- PR #36 — currentness/recovery closeout. Current Radar mailbox is `bus/radar-v2`; provider is explicitly partial/not current; recovery seed is node-bound and deliberately OFFLINE/lease-less.
- Projection anchor C — immutable trusted projector code at `f5ab21244a111b47708fa11e99d0e8ff7d8f5a45`, tree `a7dd785be8dfea883df052a73378d583e53058d1`.
- PR #37 — source-only successor to anchor C. Dispatcher, `RADAR_PROJECTION_TRUST_ANCHOR_V2.json`, and `RADAR_CURRENT.json` all bind C exactly; B is historical only.

Current PR #37 head at checkpoint creation: `7f8358afbab82f2ef7744ba1365b0deb01ea4eb2` before this checkpoint commit. Fresh-read after restore because this checkpoint commit advances the branch.

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

## Verification blocker

Hosted GitHub Actions remains broken before runner assignment. Exact-head PR #35 CI run `34049040527` created Python 3.11, Python 3.12, Edge, and SQL jobs; all completed failure with zero steps and `runner_id: 0`.

Task 10 deliberately requires a real Deno 2.9.6-generated lockfile. The current execution environment has no Deno binary/cache and outbound DNS is unavailable, so the lock was not fabricated. Until the lock is genuinely generated and the complete Python/SQL/Edge suite executes successfully, do not label the stack GREEN or runtime-qualified.

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

## Restore / continuation

On restore:

1. fresh-read `main`, PRs #33-#37, and their exact heads;
2. fresh-read issue #16 and provider migration/Edge state;
3. if hosted runners recover, generate/commit the Deno 2.9.6 lock from the pinned function config and run full Python 3.11/3.12 + SQL reset/assertions + Edge frozen-lock verification;
4. rerun the hostile invariant suite on the exact frozen candidate head;
5. keep status `SOURCE IMPLEMENTED / PROVIDER NOT APPLIED / EDGE NOT DEPLOYED / ISSUE #16 OPEN` until executable/provider evidence changes it;
6. do not merge/deploy/apply protected effects without separate Patrick authorization.

Recommended restore command:

`RADAR::RESTORE::CHAT_BUS_HARDENING_2026-09-06 — Read docs/checkpoints/RADAR_RESTORE_2026-09-06.md from the current source stack, fresh-read main, PRs #33-#37, exact-head CI, issue #16, and provider state, then continue from the verification/provider boundary. Do not invent GREEN evidence and do not merge/deploy/apply protected effects without my explicit authorization.`
