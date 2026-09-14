# VeraMesh PR #1 — Task 2 exact-head review pass

- repository: thebrazenbeard/vera-mesh
- pull request: #1
- exact head: 20b2a9b68c702d5913404b21c5bbea048f495e33
- PR state: open / draft / unmerged
- review status: TASK2_PASS / TASK10_FIXTURE_ONLY_PARTIAL

Fresh hostile review against the exact head passed:

- protocol/v1 schemas and I-JSON/JCS safe integer boundary;
- RFC 9421 P-256/P1363 profile, relay-installation binding, and exact-one RFC 9530 SHA-256 member policy;
- real pairing proof and all three receipt signatures;
- relay custody installation/key/epoch/principal trust tuple;
- exact original-inner-JWS bytes with parse/reserialize rejection;
- honest target-free runner behavior.

Exact-tree verification passed:

- protocol-object tests: 18/18;
- conformance catalog tests: 5/5;
- protocol fixture runner: 13 protocol-fixture-only PASS and 18 external-target UNRUN;
- 41 protocol/conformance/evidence file readbacks: expected blob SHA, UTF-8/LF-only, JSON parse where applicable;
- Python compilation and direct cryptographic checks: PASS.

The 18 UNRUN records are not release, runtime, device, deployment, or end-to-end evidence. No relay adapter/target, DS216, host, phone, process-death, disk/quota, upgrade/rollback, transport, or mobile exercise has been claimed.

Next active plan frontier is Task 3 source provenance. Direct inspection of vera-synology@cd0496ede55139c9309ffaff74cf9af3e781765a shows a README-declared nonfunctional Mesh scaffold (BLOCKED_MESH_NOT_IMPLEMENTED), not the VeraRelay 0.4.0 source units. The current Relay Vera Bus report remains TASK4_LOCAL_GREEN / SOURCE_UNPINNED with no Git HEAD, author identity, or remote. No source identity or registry binding is fabricated; waiting frontier is the authorized VeraRelay successor tree plus existing Git identity/remote.

No merge, deployment, SPK installation, Tailscale/network/provider mutation, credential change, or other protected effect occurred.
