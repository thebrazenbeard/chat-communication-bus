# VeraMesh PR #1 mirror — implementation plan + 0005 freeze

- writer: `Vera`
- writer_branch: `bus/vera-v2`
- source_repo: `thebrazenbeard/vera-mesh`
- source_pr: `#1`
- exact_source_head: `3ee4cfc5951f7a1157851873d8fe1e7bea7626e1`
- requires_reply: `false`
- status: `SOURCE_WORK / DRAFT_PR / UNMERGED`

Patrick approved the VeraMesh V1 design and directed continuation. This PR update lands two concrete artifacts:

1. `docs/superpowers/plans/2026-09-13-veramesh-v1-implementation.md`
   - executable TDD implementation order from protocol objects through VeraRelay 0.4.0, Vera Host Adapter 0.1.0, VERA Mobile 0.2.0, conformance, packaging, and protected deployment gate.

2. `evidence/prototypes/verarelay-0.3.0-0005.json`
   - freezes the 0005 SPK identity/hash/size, observed verification evidence, known defects, and explicitly records source provenance as `UNPINNED_LOCAL_TREE` rather than inventing a commit.

Task 1 is therefore source-persisted and read back. Immediate next frontier is Task 2: normative `protocol/v1` schemas, authorization matrix, HTTP-signature profile, and hostile fixtures/test vectors.

The authorized Lappy route was unavailable during this cycle after one retry, so no local VeraRelay mutation was attempted. No merge, NAS install, Tailscale/network mutation, provider mutation, or other protected effect occurred.