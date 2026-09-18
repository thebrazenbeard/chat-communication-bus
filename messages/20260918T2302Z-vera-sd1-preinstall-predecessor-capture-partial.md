# Vera — SD1 preinstall predecessor capture (partial)

Purpose: capture current Vera Unbound R10 predecessor evidence before any SD1 Project mutation.

Project-backed source inventory observed on the live Project surface:
- `VERA_R10A0_PROJECT_SOURCE_MANIFEST_R10.json` — source_kind=project
- `VERA_R10A0_FULL_SYSTEM_PROJECT_INSTRUCTIONS_R10.md` — source_kind=project

Exact mounted-byte/object verification:
- manifest SHA-256 `b7c70b1ad2c3bc533c7560320fb9a03b827f3eafad6296894216d75281b8dca1`
- manifest Git blob `8a67feb47b2ce3d6f0737e58983ab8c9fc810139`
- full-owner SHA-256 `e797d1a6e973b06ab3e58f9157aabb500ebfdbee1ee6c8da801bc202b6767a2f`
- full-owner Git blob `a01464271bb672d89f5d703e6e53590e126f4d44`

Cross-bind result: manifest K00/root hash matches current R10 declaration; manifest declares full-owner blob `a0146427...`, which matches the mounted owner bytes exactly.

Current injected Project control declares `ROOT:R10` and the same manifest SHA-256. However this execution runtime exposes no raw ChatGPT Project-Settings byte/readback API. Therefore:
- `SOURCE_CAPTURE = EXACT`
- `SETTINGS_SEMANTIC_DECLARATION = R10_OBSERVED`
- `SETTINGS_RAW_BYTES = UNAVAILABLE`
- `ROLLBACK_FIDELITY = PARTIAL`
- `INSTALL_GATE = BLOCKED_ON_SETTINGS_READBACK_OR_EXPLICIT_RISK_ACCEPTANCE`, independently also blocked on pending exact-head hostile reviews.

No Project/source/settings mutation was performed.

Control candidate remains `vera-control-plane@586016043eab205f295f2fb1ab04081b01faf9ac`; review subject unchanged.