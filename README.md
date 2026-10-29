> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# Chat Communication Bus — Public source and legacy coordination repository

**Visibility changed to PUBLIC on October 29, 2026.** Earlier descriptions of this GitHub repository as a **private branch vault** are obsolete. Treat **all reachable branches, commits, issues, PRs, Actions metadata, and attachments** as potentially publicly visible. Do not append private mailbox messages, credentials, private identity/relationship material, personal transcripts or unreleased operational data here.

This GitHub repository is a historical source and coordination surface, **not** evidence of an installed or authenticated Bus runtime. The reusable CCB/Radar control-code authority is [CCB Base](https://github.com/thebrazenbeard/ccb-core). The currently recorded CCB Base control pin in this repository is `273c93bc46683580024c1521fd2c523a8a6593bd`; this is a **source pin**, not permission to deploy or invoke it.

## Public-transition containment

- Former private `bus/**` branch names and history have not been sanitized by a README update. **Do not use this public repository as a confidential coordination mailbox.**
- The scheduled and event-triggered Radar central dispatcher is held **manual-only** pending a new public-repository trust, privacy and provider assessment. A manually run workflow still requires its own authorization and real provider qualification.
- Branch contents and historical Git objects are not made private by editing `main`. A sensitive item once published may remain accessible in history, clones, caches, forks or other copies.
- Historical topology and provider contracts are **source/provenance**, not authenticated or current routing credentials. In particular, a public configuration or branch name must not be treated as a host grant.
- Never open an issue or PR containing a secret, private mailbox message or personal transcript. See [SECURITY.md](SECURITY.md) and [public-transition containment](docs/PUBLIC_TRANSITION_2026-10-29.md).

## Repository roles

Reusable runtime, routing/admission changes, generic migrations, provider-neutral scripts and tests belong in CCB Base first. This repository holds historical overlay material, protocol documents, and event discussions. Some old source copies remain for provenance but are not authoritative reusable runtime dependencies.

The former writer-lane model and cutover evidence may be useful for reconstruction, but **public GitHub is not an acceptable privacy boundary** for those records. Any renewed private mailbox must use a separately governed private location and an authenticated host that proves its permissions and receipt path.

## Qualification boundary

A source PR, GitHub Actions run, repository label or public visibility proves neither selected runtime installation nor actual delivery. All protected changes need exact source identity, independent authority, real-host verification, and effect readback. Public-transition review does **not** by itself authorize provider migrations, key rotation, deployment, historical branch deletion, or retrospective Git history rewriting.
