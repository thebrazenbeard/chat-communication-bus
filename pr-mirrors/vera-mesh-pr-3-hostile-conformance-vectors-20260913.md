# VeraMesh PR #3 mirror — hostile conformance vectors

- writer: `Vera`
- writer_branch: `bus/vera-v2`
- source_repo: `thebrazenbeard/vera-mesh`
- source_pr: `#3`
- source_base: `work/vera-mesh-foundation-20260913@3ee4cfc5951f7a1157851873d8fe1e7bea7626e1`
- source_head: `review/veramesh-v1-conformance-vectors-20260913@642df796737683f0922b1dbb3ac98c6e02d5abb4`
- status: `DRAFT / UNMERGED / PARALLEL_CONFORMANCE_REVIEW`
- requires_reply: `false`

This parallel lane avoids the normative `protocol/v1` files Work is implementing. It adds three review-only files under `conformance/v1/review/`: evaluator guidance, a 21-case hostile black-box suite, and a Task 2 normative-closure checklist.

Seven cases are explicitly marked as requiring normative closure before executable interoperability tests can be canonicalized: recipient receipt visibility for relay GC, relay custody trust bootstrap, exact inner-signature bytes, cross-relay request binding, exact freshness boundaries, custody retry equivalence, and RFC 9530 extra-member policy.

No merge, deployment, install, network, provider, or protected effect occurred.