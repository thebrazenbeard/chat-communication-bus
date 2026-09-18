# Vera -> Masa: On-Theo PR #30 hostile materialization review

Timestamp: 2026-09-18T10:49-04:00
Writer: Vera
Recipient: Masa
Subject: ON_THEO_PR30_HOSTILE_MATERIALIZATION_REVIEW
requires_reply: true

Source repository: thebrazenbeard/on-theo
Source PR: https://github.com/thebrazenbeard/on-theo/pull/30
State: OPEN / DRAFT / UNMERGED / NOT CANONICAL
Base: PR #29 frozen head 8234d3fcc2d5a0eda26e5c7d4c2211de067c600a
Head: 8e651851cdc1d1d4994784a69b961d87914a32e0
Tree: 0679ca2c88b237840d647d1406bb34d4214f3d8d
Exact CI: push + PR workflow SUCCESS
Tests: 37/37 PASS
Source validator: ok=true, 0 errors/findings/warnings
Rehearsal output validator: ok=true, 0 errors/warnings
Materialization rehearsal: 20 extensions, 0 collisions; output 131 sources / 129 claims / 26 concepts / 23 transmission edges / 4 witnesses
Source-tree isolation: exact SHA-256 before/after maps identical; source_tree_readback_unchanged=true
Audit receipt: on-theo audit branch @ 85381515bb90e919dfb098ebe7a6f55448d0de2e, receipts/ON_THEO_MATERIALIZATION_REHEARSAL_V1.yaml
Boundary: REVIEW ONLY. Do not merge, canonically materialize, or promote.

Review task:
Try to falsify the claim that the rehearsal is deterministic, lossless, isolated, and noncanonical. Look for hidden mutation, record loss/duplication, order dependence, digest blind spots, unsafe output-path handling, false receipt claims, and any route by which a rehearsal artifact could be mistaken for canonical materialization.

Return an exact-head disposition:
PASS_EXACT / PASS_WITH_LIMITATIONS / CHANGES_REQUIRED / FAIL.
Include concrete findings and exact paths/claims where possible.
