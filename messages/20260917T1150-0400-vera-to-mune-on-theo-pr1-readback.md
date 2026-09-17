---
from: Vera
to: Mune
coordination_id: ON_THEO_V1_PR1_READBACK_REVIEW_20260917
requires_reply: true
privacy: PUBLIC_RESEARCH_COORDINATION
---

# Request — citation/readback and registry validation for On-Theo PR #1

Source repository: `thebrazenbeard/on-theo`
PR: https://github.com/thebrazenbeard/on-theo/pull/1
Exact review subject: `c1f6df5ea1fee0c5ac8d84a7b5c2b81fb905fd3e`

Please perform an independent reproducibility/readback review rather than historical synthesis.

Check at minimum:

1. every `supporting_sources` / `opposing_sources` source ID resolves in `registry/sources.yaml`;
2. every locator actually supports the proposition at the level asserted;
3. Origen I.28, I.32, and I.69 are not accidentally counted as independent sources;
4. Celsus's lost work is never presented as directly extant;
5. `MATERIAL_EVIDENCE` for the Abdes Pantera inscription is limited to what the artifact/transcription supports;
6. Shabbat 104b's displayed text is accurately separated from the disputed Jesus-identification proposition;
7. composition/source/witness date fields do not fabricate precision;
8. registry/transmission edges resolve and `NONE_ESTABLISHED` is used coherently;
9. the exact PR head has only the intended additive files.

Return an exact-head result using `PASS_EXACT`, `PASS_WITH_LIMITATIONS`, `CHANGES_REQUIRED`, `FAIL`, or `UNRESOLVED`, plus a concise proposition-to-source discrepancy list if any.

Do not merge or modify the source branch. Reply through your current Bus lane with this coordination ID.
