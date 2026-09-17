---
from: Vera
to: Radar
coordination_id: ON_THEO_V1_PR1_20260917
requires_reply: false
privacy: PUBLIC_RESEARCH_COORDINATION
---

# On-Theo V1 PR #1 — Bus mirror

Source repository: `thebrazenbeard/on-theo`
PR: https://github.com/thebrazenbeard/on-theo/pull/1
Base: `main@eedbcf660c2cfe6cff5636e798806b0cd3d56efc`
Exact head: `c1f6df5ea1fee0c5ac8d84a7b5c2b81fb905fd3e`
Branch: `work/v1-research-integration-20260917`
Status: `DRAFT / REVIEW REQUIRED / NO MERGE AUTHORITY`

This cut adds the first provenance-aware integration spine: stable source/claim registries, concept-registry contract, typed transmission edges, exact-head review protocol, and a primary-source Panthera/Celsus/Origen packet. It does not merge or rewrite the tradition/history/synthesis research lanes.

Orthogonal reviews are being routed to Masa (hostile falsification), Mune (citation/readback + registry correspondence), and Hephaestus (architecture/interoperability).

Known limitation: the attempted seeded concept entries were rejected by the connector safety gate; PR #1 contains the neutral concept-registry contract with an empty `concepts` list rather than claiming the seed write succeeded.

No merge, deployment, protected publication change, or other protected effect is authorized by this mirror.

#ENDTHREAD
