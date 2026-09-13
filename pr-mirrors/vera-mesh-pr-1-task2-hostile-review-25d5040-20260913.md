# VeraMesh PR #1 Task 2 hostile review mirror

- writer: `Vera`
- writer_branch: `bus/vera-v2`
- source_repo: `thebrazenbeard/vera-mesh`
- source_pr: `#1`
- exact_reviewed_head: `25d5040c4898f6fe4bde8bf540fe9ed7b985ba2d`
- source_review_id: `5192763583`
- verdict: `FIX_BEFORE_TASK2_CLOSE`
- requires_reply: `false`

Exact-head hostile review found concrete Task 2 interoperability/security defects without reopening the approved architecture:

1. Pairing nested proof has no normative signature base; the fixture labeled valid uses an all-zero P1363 signature and tests never cryptographically verify it.
2. AAD/envelope hash serialization exists only in the Python `canonical_json()` test helper, not as a normative cross-language byte rule.
3. Receipt P1363 signatures have no normative signature base; hostile cross-field signer/key/recipient mismatch fixtures are absent.
4. Protected HTTP signatures still lack relay/destination binding, leaving the prior cross-relay replay issue open.
5. Pairing/bootstrap still lacks a normative `relay_installation_id -> relay custody public key + epoch` trust binding.
6. Content-Digest extra-member policy, custody-retry equivalence, exact inner-signature bytes, and relay-GC use of recipient-storage evidence remain underspecified. Freshness boundaries are now concretely specified.
7. Authorization matrix exposes `/v1/health` unauthenticated despite the approved role/status model and transport-not-authorization boundary; narrow public health or restore role/scoped status semantics.
8. Nonce generation should require >=16 CSPRNG bytes; verifier can check length/encoding/uniqueness, not entropy itself.

Parallel review PR #3 also now contains 36 hostile/recovery review cases and traceability coverage. No merge, deployment, install, network, provider, or other protected effect was performed.
