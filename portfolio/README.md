# Public portfolio metadata and bounded evidence

These files are public-safe *source snapshots* for the `project_unfuck_runtime_coordination` event. They are not a dependency resolver, current host topology, permission grant, or deployment record.

- [`PUBLIC_ONLY_OWNER_INVENTORY_V1.json`](PUBLIC_ONLY_OWNER_INVENTORY_V1.json) captures 91 public repositories, each with the observed default-branch commit SHA, plus aggregate counts (without names or other identifying metadata) of 18 private repositories. The snapshot is time-bound. It preserves the three public archived repositories as archived entries.
- [`PUBLIC_ECOSYSTEM_EDGE_EVIDENCE_V1.json`](PUBLIC_ECOSYSTEM_EDGE_EVIDENCE_V1.json) captures four *sampled* public associations and their source-file blob pins. `DOC_LINK` is not a declared dependency; `UNKNOWN` explicitly does not establish a dependency, adapter or installed integration. The evidence-class field keeps documentation separate from packaging metadata, executable tests and host probes.

## Reproduce or refresh

1. Re-enumerate repository metadata with an authenticated, owner-scoped GitHub connection. Public repository membership, default branch and archive state are visibility-sensitive and can change. Keep private information as **aggregate counts only**.
2. For each *public* repository, read `GET /repos/thebrazenbeard/<repo>/branches/<default-branch>` and record `commit.sha` at an observation timestamp. Repositories may advance during collection; this is a snapshot, not an atomic multi-repository transaction.
3. For any proposed relation, inspect the exact source commit and record a source blob SHA and the narrowest defensible evidence class. Do not turn README links, local imports or package-name overlap into host authority.
4. Run `python -m pytest -q tests/governance/test_public_only_owner_inventory.py tests/governance/test_public_ecosystem_edge_evidence.py`. A passing local test checks schema and disclosure invariants only; live GitHub membership, package installation and physical host behavior need separate verification.

Public source and issue metadata are not a confidential coordination bus. Do not add private repo names, host identifiers, credentials, transcripts, or sensitive relationship and memory records here. License and contribution terms remain those of the repository root.
