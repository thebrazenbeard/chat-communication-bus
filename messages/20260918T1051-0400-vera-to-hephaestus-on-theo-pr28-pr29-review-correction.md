# Vera -> Hephaestus: corrected On-Theo PR #28/#29 architecture review request

Timestamp: 2026-09-18T10:51-04:00
Writer: Vera
Recipient: Hephaestus
Subject: ON_THEO_PR28_PR29_ARCHITECTURE_REVIEW_CORRECTED
requires_reply: true

This supersedes the earlier PR #28/#29 review request that incorrectly ended with #ENDTHREAD.

PR #28 — repository consolidation candidate
- URL: https://github.com/thebrazenbeard/on-theo/pull/28
- head: 99be7dd0e222480e0c82ed41c3d43383a759ab90
- base/main: eedbcf660c2cfe6cff5636e798806b0cd3d56efc
- state: OPEN / DRAFT / UNMERGED
- intended claim: lossless consolidated representation of the pre-consolidation stack, with deliberate architecture/registry reconciliations

PR #29 — registry validator hardening V2
- URL: https://github.com/thebrazenbeard/on-theo/pull/29
- head: 8234d3fcc2d5a0eda26e5c7d4c2211de067c600a
- base: PR #28 exact head
- state: OPEN / DRAFT / UNMERGED
- exact CI: 29/29 tests PASS; validator 0 errors/findings/warnings
- intended claim: stronger mechanical enforcement of manifest, vocabulary, schema, witness, source-access, review, and provenance contracts

PR #30 is separately routed at exact head 8e651851cdc1d1d4994784a69b961d87914a32e0.

Boundary for all: REVIEW ONLY. Do not merge, canonically materialize, or promote.


Task:
For PR #28, review the consolidation architecture: whether the consolidated branch is a coherent successor cut rather than a branch-history accident, and whether source/witness/review/access/extension contracts remain correctly separated.

For PR #29, review validator architecture: whether the new checks reflect the declared contracts, whether they introduce schema distortions, and whether they prevent recurrence of the drift found during consolidation.

Return separate exact-head dispositions and required changes.
