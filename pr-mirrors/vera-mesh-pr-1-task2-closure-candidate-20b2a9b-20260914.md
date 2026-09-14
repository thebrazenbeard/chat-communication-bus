# VeraMesh PR #1 — Task 2/10 closure candidate

- repository: thebrazenbeard/vera-mesh
- pull request: #1
- head: 20b2a9b68c702d5913404b21c5bbea048f495e33
- state: open / draft / unmerged
- predecessor head at start of repair: ce9bcbc44b7d947c2475cb3af3b06a10f14bc515

## Task 2 closure slice

Normative protocol/v1 schemas, authorization matrix, RFC 9421 HTTP-signature profile, exact inner-envelope/JCS serialization profiles, signed pairing/receipt profiles, hostile fixtures, and fixed interoperability vectors are present. The closure includes:

- exact relay-installation binding in protected request coverage;
- exact-one SHA-256 Content-Digest policy;
- real P-256/P1363 pairing and receipt vectors;
- custody trust bootstrap bound to installation/key/epoch/principal and actual signed receipt bytes;
- exact original inner-JWS payload bytes;
- I-JSON/JCS safe-integer boundary enforcement at 2^53-1 with hostile fixture/vector.

Target-free checks on the exact tree:

- protocol-object tests: 18 passed;
- conformance catalog tests: 5 passed;
- protocol fixture runner: 13 PASS with qualification_scope=protocol-fixture-only;
- external-target cases: 18 UNRUN;
- all 41 protocol/conformance/evidence readbacks: expected blob SHA, UTF-8, LF-only, JSON parse where applicable.

The fixture runner does not claim VeraRelay runtime, DS216, phone, host, deployment, or end-to-end conformance.

## Task 3 frontier

The available vera-synology branch feature/mesh-ds216-target-first-repair-v1 at cd0496ede55139c9309ffaff74cf9af3e781765a is explicitly a nonfunctional Mesh scaffold (BLOCKED_MESH_NOT_IMPLEMENTED), not the authorized VeraRelay 0.4.0 successor source. No source identity or implementation registry binding was fabricated. Task 3 remains source-route blocked pending the authorized local VeraRelay successor tree and existing Git identity.

No merge, deploy, SPK installation, Tailscale/network/provider mutation, credential change, or other protected effect was performed.
