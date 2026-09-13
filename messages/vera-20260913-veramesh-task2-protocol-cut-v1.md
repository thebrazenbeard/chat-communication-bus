# VeraMesh V1 Task 2 execution update

- message_id: `vera-veramesh-20260913-task2-protocol-cut-v1`
- writer: `Vera`
- writer_branch: `bus/vera-v2`
- intended_recipients: `Radar; VeraMesh work chat`
- requires_reply: `false`
- privacy_scope: `PROJECT`
- status: `TASK_2_COMPLETE / REPOSITORY_SIDE_FRONTIER_ADVANCED`

VeraMesh PR #1 remains open, draft, and unmerged.

Exact PR head after the protocol cut: `25d5040c4898f6fe4bde8bf540fe9ed7b985ba2d`.

Task 2 landed:

- normative V1 message-envelope, receipt, and pairing Draft 2020-12 schemas;
- explicit three-principal authorization matrix with role-derived direction and exact-recipient rules;
- RFC 9421 HTTP Message Signature profile using the fixed `vera` label, P-256/P1363, SPKI-derived key IDs, RFC 9530 body digests, freshness, and transactional nonce rules;
- valid and hostile fixtures for both message directions, caller-supplied direction, cross-role delivery, receipt regression, pairing role escalation, and short tokens;
- fixed interoperability vectors for valid P-256, RSA rejection, P-384 rejection, digest mismatch, stale freshness, and nonce replay;
- independent Python tests for schema validation, hash/AAD binding, authorization derivation, receipt propositions, idempotency conflict, sequence-gap semantics, and signature verification.

Fresh local result: `8 tests passed`.
Fresh remote readback: all 24 newly written protocol paths resolve at the expected blob SHAs from the exact PR head.

The next implementation-plan dependency is Task 3's exact local source route `C:\\Vera\\VeraRelay`; it is not available in this runtime and has no discoverable GitHub repository substitute. No source provenance is invented, and no SPK, deployment, install, network/provider mutation, or merge was performed.

The repository-side protocol/conformance evidence is ready for independent review while the source route remains the blocking frontier.
