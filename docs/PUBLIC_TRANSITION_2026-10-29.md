# Public-visibility transition: containment record (2026-10-29)

**Observed GitHub state at start of this response:** `thebrazenbeard/chat-communication-bus` was `public`, `main@eca2b241683ad1681df08606c381e44717b8dc8d`, with no advertised branch protection or repository rulesets. A direct branch-protection API request returned 403 to the connector, so protection settings beyond the returned metadata are **UNKNOWN**.

The existing `README.md` still claimed this was a *private branch vault*. Its `bus/**` branches, historic commits and checkpoint/issue surfaces must now be treated as externally accessible. A bounded scan of 276 readable text files in a fresh shallow `main` checkout did not match selected common private-key, GitHub-token, service-role, or JWT patterns. **This was not an exhaustive secret scan**, did not inspect other branches, Issues, full historical commits, provider values, or caches, and is not evidence of no exposure.

The repository retains historical private-branch assumptions in its topology/operator documentation and runnable infrastructure. Do **not** mark a mailbox, endpoint, identity, or installed provider private solely because source documentation uses the word `private`.

## Immediate source-only containment in this patch

1. Replace the top-level private-vault claim with an explicit PUBLIC warning and CCB Base source role.
2. Add SECURITY.md with no-public-secret disclosure rules and guidance for externally copied material.
3. Disable automatic `workflow_run` and five-minute `schedule` triggers from the default-branch Radar Central Dispatcher; retain only `workflow_dispatch` as a deliberate **manual trigger**, not deployment approval.
4. Add CI source tests to prevent regressions in these minimal public-transition safeguards.

**Not accomplished by source updates:** repository visibility change; branch deletion/force push; historical rewrite; GitHub ruleset configuration; GitHub security settings; secret rotation; issue redaction; Supabase provider trust change; installed workflow cancellation; live peer acknowledgment; canary; private data recall. Treat these as separate tracked operator actions, each with exact-target authority and readback.

## Required owner/provider follow-through

- Conduct a restricted inventory of **all refs**, issues, PRs, Actions logs/artifacts, releases, attachments, and reachable Git history. A public Git repository can no longer function as a private mailbox, even if `main` looks clean. Public-source code hosting and private correspondence need separate access domains.
- Determine whether any *real* credentials, token issuers, audience/trust assumptions, private conversation records or personally identifiable material were exposed. If so, coordinate revocation/rotation and privacy response through the affected provider/owner. Do not publish discovered values into an audit.
- Decide whether formerly private `bus/**` mailboxes must move to a new private repository/service. Make explicit how source custody, message receipts, branch references and immutable historical evidence will be retained. Migrations cannot erase already distributed copies.
- Independently inspect the default-branch projector OIDC binding, public fork threat model, provider actual migration/config state, and intended private data destination before reinstating automated triggers.
- Apply branch protection/ruleset and security scanning settings through authorized GitHub administration; this source patch cannot enforce repository settings.
- Never merge historical executable VS Code task loaders or branch-only automation from `bus/**` into publicly used `main` without a targeted security review.
- Fresh-read and independently qualify [CCB Base](https://github.com/thebrazenbeard/ccb-core) source/host integration; no runtime effect or deployment is implied here.

## Evidence boundary

**DOC + SOURCE_TEST only.** A passing GitHub Actions run would demonstrate this repository's source test under a hosted runner, not provider safety or the confidentiality of the newly public history. Use `docs/operator/RECOVERY.md` and current owner authority for actual runtime operations. Preserve event `project_unfuck_runtime_coordination` as the coordination referent, but do not equate an issue comment with a private authenticated message.
