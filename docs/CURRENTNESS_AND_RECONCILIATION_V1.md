# Chat Communication Bus Currentness and Reconciliation V1

Status: **DRAFT / PREPARED FIRST-PARENT SOURCE / NOT CANONICAL**

Canonical `main` is now
`f9179bd1426bf90c23ab6a4d14d5a8e9b39c66d2`, tree
`a57369a6fab68d7bc2a3d2f4999aace7c317486c`.

That main still contains issue #79's wrong-target Brigit path
`messages/brigit-20260910-roommate-chaos-1244.md`, but it also contains a later
legitimate source change from PR #300: replay-guard RLS hardening.

The old PR #194 reconciliation source is therefore stale as a complete result
tree: it correctly excludes the wrong-target path, but it predates the RLS
migration and regression test now present on canonical main.

The refreshed prepared first-parent source is:

- branch: `bt2/bus-canonical-main-reconciliation-v2-source-20260922`
- exact executable/source commit:
  `7ec2860c2bf32404a70bd5f1b6a08d3f73ab6e9c`
- tree: `d81306c749b6864f6e08a53c66599f5d0ca66d19`
- source parent lineage: PR #194 repaired tree/documentation line
- intended future second parent if separately authorized:
  `f9179bd1426bf90c23ab6a4d14d5a8e9b39c66d2`

The prepared tree:

- keeps the Anchor-E central dispatcher blob
  `c164a354bd70a67d009d0947243ae8581e41c178`;
- keeps PR #300 migration blob
  `054d668486887c05efe359314b51894e7274d0a6`;
- keeps PR #300 regression-test blob
  `03d9759b80af5648748aa4630be88216a1de550e`;
- updates `EXPECTED_RADAR_MIGRATIONS` to include
  `20260922171230_radar_oidc_replay_guard_rls_v1.sql`;
- excludes the wrong-target Brigit message path.

No two-parent reconciliation commit was constructed. That is intentionally
left behind the protected merge/current-main gate. Before any future
canonicalization, current `main` must be fresh-read again and this source tree
must receive exact execution/review evidence appropriate to its changed bytes.

Provider recovery remains a separate axis. The live provider has already
advanced to the six-migration + Edge-v4 state recorded in issue #16; canonical
caller/workflow convergence is not proven merely by preparing this source tree.

No merge, main ref move, provider/cursor mutation, topology activation, branch
deletion, workflow dispatch, or other protected effect is authorized or
performed by this candidate.
