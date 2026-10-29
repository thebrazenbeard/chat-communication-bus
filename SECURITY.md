# Security and public repository disclosure

**As of 2026-10-29, this repository is PUBLIC.** The previous private-overlay designation is historical and does not restrict GitHub access. A source-visible/proprietary license does not provide confidentiality.

## Report a security concern

Use GitHub's **Report a vulnerability** / private vulnerability reporting feature **if available on this repository**, or contact the repository owner through a previously trusted private channel. **Do not post credentials, private messages, personal records, exploit tokens, or vulnerability reproduction details that expose them in public Issues, Discussions, PRs or comments.** Do not assume this repository has a configured private-advisory channel until you verify it.

## Exposure and containment

Assume a person outside the project may access public branches, commit history, GitHub issue/PR timelines, and Actions logs or artifacts. A new commit removing content does not revoke Git objects, snapshots, existing clones, forks, exports, notifications, or search-engine caches.

If material was supposed to remain confidential, triage it as an **already public exposure**. Inventory affected refs and surfaces without reposting contents, revoke or rotate any *actual* exposed credentials via the relevant provider, rebind trust/permissions, and obtain the affected parties' required privacy handling. Do not claim that secret scanning or changing a README has undone exposure.

Do not force-push, mass-delete branches, rewrite history, or disable required provider services as a blind repair. Such operations can break coordination, cannot erase already fetched copies, and require an explicit owner-approved migration, custody inventory and verification.

## Automation

Until the public transition is qualified, the source central dispatcher is intentionally **manual-only**. Other legacy workflows, historical trust anchors and source configs are not declarations of a safe active production pipeline. Do not invoke a manually runnable workflow, change an OIDC trust relationship, or deploy to Supabase without specific operator authority, current host and provider evidence and rollback/readback.

## Safe contribution boundary

Public source and tests only. Keep private communication and credential-bearing material in a separately authorized private system. Never infer that source visibility grants usage or model-training rights; see [LICENSE](LICENSE).
