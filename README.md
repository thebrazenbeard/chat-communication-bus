> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# Chat Communication Bus — Private Branch Vault

This private repository is no longer the reusable CCB/Radar code authority.

The operational source of truth is **CCB Base**, currently hosted at `thebrazenbeard/ccb-core`. Private branch automation is pinned to qualified CCB Base revisions rather than executing reusable control code from this repository.

## What belongs here

- private `bus/**` writer lanes and other private work branches;
- private topology and cutover state;
- private identity/deployment overlays, checkpoints, receipts, and recovery evidence;
- OIDC/provider workflow context that must remain bound to this private repository;
- retained historical source and branches for provenance.

## What does not become canonical here

Generic runtime fixes, routing/admission changes, reusable migrations, provider-neutral scripts, and regression tests belong in CCB Base first. Existing copies in this repository are legacy/history unless a private overlay specifically requires them.

Current qualified CCB Base pin for branch control: `273c93bc46683580024c1521fd2c523a8a6593bd`.

## Flow

A private branch can expose a defect, but the reusable fix is sanitized, tested, and committed to CCB Base. Private workflows then advance their explicit CCB Base pin. Private topology remains data; it is not a second implementation authority.

No history is deleted by this role change.

## Private-overlay qualification

Private repository CI validates the overlay boundary, exact CCB Base control pin,
and explicit private topology/cutover inputs. Reusable Python runtime, Edge, and
SQL implementation qualification belongs to CCB Base and is not duplicated here.
