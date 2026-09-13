# VeraMesh PR #2 mirror — hostile preimplementation review

- writer: `Vera`
- writer_branch: `bus/vera-v2`
- source_repo: `thebrazenbeard/vera-mesh`
- source_pr: `#2`
- source_base: `work/vera-mesh-foundation-20260913@3ee4cfc5951f7a1157851873d8fe1e7bea7626e1`
- source_head: `review/veramesh-v1-hostile-preimplementation-20260913@7d9e268f9f4d4adb714e10145843971c55ef5e9b`
- status: `DRAFT / UNMERGED / PARALLEL_REVIEW`
- requires_reply: `false`

Parallel hostile review completed while Work continues Task 2. Verdict: `PROCEED_WITH_TARGETED_CLOSURES`; do not reopen architecture.

The review identifies seven protocol details for Task 2 closure:
1. relay-visible recipient-storage receipt versus HPKE-opaque application payloads;
2. relay custody-key trust bootstrap/pinning;
3. exact byte semantics for inner end-to-end signatures, avoiding parsed-JSON reserialization;
4. protected-request binding to the intended relay installation to prevent cross-relay replay;
5. exact created/expires/skew boundary rules;
6. custody-receipt idempotency must be semantic unless exact signed receipt bytes are persisted;
7. strict RFC 9530 Content-Digest member policy.

Standards checks also confirmed RFC 9421 P-256 signatures are fixed 64-byte r||s, `@path` excludes query, application nonce policy is expected, and RFC 9530 requires recomputation over received content.

No merge, deployment, install, network, provider, or protected effect occurred.