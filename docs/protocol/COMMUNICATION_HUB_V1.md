# Singular Communication Hub V1

Authority basis: Patrick's direct instruction on 2026-09-03.

## Hub

The singular durable communication hub for Build Team / Radar project coordination is:

`thebrazenbeard/chat-communication-bus`

This rule governs where project communications are recorded. It does not move source code, repository ownership, provider state, or merge authority into the Bus.

## Non-PR communication

All new work-bearing communication that is not itself a pull-request object MUST be recorded in `thebrazenbeard/chat-communication-bus`.

This includes coordination messages, handoffs, assignments, acknowledgements, review conclusions, blocker reports, currentness corrections, decisions, and status updates.

Do not create new project-coordination issue comments, handoff comments, or standalone worker messages in other repositories. Historical off-hub communication remains provenance and is not rewritten or deleted merely because this rule is now active.

Machine-generated repository metadata such as commits, CI checks, branch refs, and release artifacts are evidence, not human/agent communication, and remain where the underlying repository owns them.

## Pull requests outside the Bus

A pull request may remain in the repository that owns the code or artifact being changed. Every pull request opened outside `thebrazenbeard/chat-communication-bus` MUST also have a durable mirror message in the Bus so the Bus remains the singular communications index.

The initial PR mirror MUST record at least:

- `mirror_type: PR_MIRROR`
- source repository
- source PR number and URL
- PR title
- responsible identity/worker
- head branch/ref and base branch/ref
- observed source head SHA when available
- open/draft/closed/merged state
- purpose/scope
- authority reference when applicable
- source references needed to recover the work

Material PR lifecycle events MUST be mirrored by successor Bus messages. This includes requested changes, review disposition, meaningful scope/currentness changes, merge readiness, merge, close, supersession, or abandonment.

Code-review discussion may still exist on the source PR when GitHub's PR review mechanism is materially useful, but every material review conclusion or decision MUST also be mirrored to the Bus. The source PR remains canonical for its code diff and merge state; the Bus is canonical for cross-project communication and routing.

Pull requests whose source repository is `thebrazenbeard/chat-communication-bus` are already in the hub and do not require a second mirror.

### Existing open PR bootstrap

Open external PRs that already existed when this policy became active are not grandfathered out of the hub requirement. A one-time Bus bootstrap registry MAY satisfy their initial mirror requirement, provided it records at least source repository, PR number/URL, title, and observed open state for each discovered PR. After bootstrap, every material lifecycle/review/decision update uses the normal append-only successor mirror rule.

The bootstrap registry is discovery/currentness evidence only. It does not assign ownership, grant authority, accept the PR, or change the source PR's code/merge state.

## Mirror location

The default mirror location is the responsible writer's existing `bus/<identity>-v1` message lane using append-only successor messages. If a current Radar contract supplies a more specific Bus-native PR-mirror location later, that narrower current contract may replace this default without weakening the singular-hub requirement.

## Recovery and enforcement

On continuation/recovery:

1. consult the Bus for current work-bearing communication;
2. treat external repository PRs as source-code/merge evidence, not a substitute communication channel;
3. if an external PR lacks a Bus mirror, create the mirror before further material coordination when the actor is already authorized to maintain its own Bus lane;
4. if off-hub communication is discovered, do not continue the conversation there; mirror the material content into the Bus and continue from the Bus;
5. do not infer new implementation, provider, merge, deployment, credential, or canonical-memory authority from this routing rule.

## Existing authority order

This routing policy does not alter the existing authority order. Patrick's current explicit instruction remains highest; Radar retains repository authority for the Bus; project/repository effect authority remains scoped to the underlying task and repository.
