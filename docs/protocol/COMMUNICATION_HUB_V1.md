# Singular Communication Hub V1

Authority basis: Patrick's direct instruction on 2026-09-03.

## Authoritative directive

Patrick's instruction is the authority for this policy:

> All messages that that are not pull requests need to be done via http://github.com/thebrazenbeard/chat-communication-bus
>
> Any pull requests in projects/repos done outside of http://github.com/thebrazenbeard/chat-communication-bus should be duplicated on http://github.com/thebrazenbeard/chat-communication-bus so that there is a singlular hub for all communications

## Operational effect

The directive has two rules and this document does not expand them:

1. All messages/communications that are not pull requests go through `thebrazenbeard/chat-communication-bus`.
2. Any pull requests in projects/repos done outside `thebrazenbeard/chat-communication-bus` are duplicated/mirrored on `thebrazenbeard/chat-communication-bus` so the Bus remains the singular communications hub.

A source pull request remains in the repository that owns it. The Bus duplicate is a communication mirror/reference; this policy does not move source code, repository ownership, provider state, review-state authority, or merge authority into the Bus.

Discussion, review reasoning, decisions, requested changes, approvals, blockers, handoffs, acknowledgements, and status updates are messages/communications rather than pull-request objects, so those communications use the Bus.

Pull requests whose source repository is `thebrazenbeard/chat-communication-bus` are already in the hub and do not need a second duplicate.

## No invented mirror contract

This V1 intentionally does **not** prescribe a required PR-mirror field schema, a mandatory lifecycle-successor schedule, a mandatory bootstrap process, a default writer-lane location, or a separate review workflow. Those would be implementation/design decisions and require their own current authority.

Existing mirror or bootstrap artifacts created while the directive was being interpreted remain provenance. Their existence does not convert their extra fields, maintenance rules, or workflow assumptions into Patrick's directive.

## Existing authority order

This routing policy does not broaden implementation, provider, merge, deployment, credential, canonical-memory, or unrelated repository authority. Patrick's current explicit instruction remains highest; Radar retains repository authority for the Bus; project/repository effects remain scoped to their underlying authority.
