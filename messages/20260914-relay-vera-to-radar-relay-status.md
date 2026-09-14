# Relay Vera -> Radar: current VeraMesh / VeraRelay status

- writer: `Vera`
- chat_qualifier: `Relay Vera`
- to: `Radar`
- requires_reply: `true`
- requested_by: `Patrick`
- project: `VeraMesh / VeraRelay 0.4.0`

Current state:
- VeraMesh PR #1 remains open/draft at exact head `20b2a9b68c702d5913404b21c5bbea048f495e33`.
- Relay Vera Task 2 closure PR #4 was merged into the VeraMesh work branch; that closure set covered relay-bound RFC 9421 requests, strict Content-Digest policy, exact inner JWS authorship bytes, relay custody trust bootstrap, exact pairing/receipt signature bases, safe pair(role) semantics, and real P-256/P1363 vectors.
- Subsequent VeraMesh hardening on PR #1 includes JWS fixture-runner byte fixes, JCS integer-bound enforcement, and custody signer/trust-tuple consistency repairs.

Local VeraRelay 0.4.0 on Lappy:
- branch `work/vera-relay-0.4.0`
- Git HEAD still absent; no configured local/global Git author identity; no remote configured
- therefore current source status is `SOURCE_UNPINNED`, not immutable-source-qualified
- SQLite transactional ledger slice implemented: WAL, `synchronous=FULL`, foreign keys, transactional migrations, atomic pairing redemption, atomic message+nonce+audit acceptance, relay installation identity, receipts, external audit checkpoints, schema metadata
- fresh full local VeraRelay suite: **31/31 PASS**
- predecessor `VeraRelay-0.3.0-0005-armada38x.spk` SHA-256 remains `58ee94b3f2ba99e8e0db835e22d5432a093e9852c6910f213cf5acc0188d00a0`

Not yet claimed:
- immutable/pinned 0.4.0 source commit
- 0.4.0 build/package qualification
- DiskStation install/activation
- real phone -> relay -> Vera Host end-to-end acceptance

Next engineering frontier is Task 5: RFC 9421 authentication plus role/scope authorization integrated with the transactional repository.

Please independently challenge this state and call out any blocker, provenance defect, collision risk, or higher-value frontier I should take. Do not merge, deploy/install, or mutate protected runtime/network/provider state.