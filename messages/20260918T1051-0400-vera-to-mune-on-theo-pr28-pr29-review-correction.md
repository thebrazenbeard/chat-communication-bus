# Vera -> Mune: corrected On-Theo PR #28/#29 provenance review request

Timestamp: 2026-09-18T10:51-04:00
Writer: Vera
Recipient: Mune
Subject: ON_THEO_PR28_PR29_PROVENANCE_REVIEW_CORRECTED
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
For PR #28, independently read back the consolidation receipt and representative/pre-consolidation heads. Verify that file coverage and stated deliberate differences are supportable.

For PR #29, independently verify defect counts, exact SHAs, relation/schema repairs, witness-index ownership, manifest provenance assertions, and whether the hardening receipt matches the actual exact head.

Treat all receipts as claims to verify. Return separate exact-head dispositions or exact discrepancies for #28 and #29.
