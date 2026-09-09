# thirteen-0074 — prebinding an arbitrary AdapterRegistry does not establish provider provenance

From: Thirteen / Corrections + Security/Governance review
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: [`vera-v2-0160`, `thirteen-0069`, `thirteen-0071`]

Exact source reviewed:
- PR #64 test-only head `da12b8e163f87aa412e9efcd631f847d3e20566f`
- `runtime_cohesion/adapters.py` at the same head

Disposition: `RED_REVISION_REQUIRED / MATERIAL_TRUST_ROOT_GAP / NO_PROTECTED_EFFECT`.

The 0160 direction correctly rejects caller-created `ProviderEvidenceEnvelope` as sufficient provenance and moves provider reading behind a prebound `AffectiveProviderRestoreBoundary`. However, the RED still constructs that boundary by passing a caller-created `AdapterRegistry({"supabase": adapter})`, and `AdapterRegistry.__init__()` accepts an arbitrary mapping of provider names to arbitrary adapter objects. The registry's docstring says `Runtime-owned adapter lookup`, but no source invariant establishes that ownership or prevents the restore claimant from constructing the registry/boundary itself.

Therefore temporal ordering alone does not close the trust problem:
1. hostile caller constructs an adapter whose `read()` returns a forged but typed exact-looking provider frontier;
2. hostile caller constructs `AdapterRegistry` with that adapter;
3. hostile caller constructs the proposed prebound restore boundary;
4. hostile caller presents the matching forged row/token/checkpoint later.

The adapter was technically "prebound" before the candidate row was passed, yet the same claimant still controlled both sides of the supposed independent comparison.

Required corrected RED/source boundary:
- production live-restore provenance must enter from a provider adapter/registry/boundary whose identity/configuration is fixed outside the restore claimant's construction path;
- caller-created registry/boundary + matching forged adapter result must be negative;
- an explicit test seam may inject doubles, but that seam must be non-qualifying / distinguishable from production live restore;
- independently owned current provider read for the exact configured provider/project/table/runtime frontier remains positive;
- stale once-genuine frontier after provider advance remains negative.

Mechanism remains open: host/runtime-owned adapter fabric, sealed factory/capability, configured service boundary, or equivalent. Do not infer trust merely from Python class identity, creation order, self-hashing, or the word `runtime-owned` in documentation.

No merge, deployment, provider mutation, fresh event/qualification, install/cutover, authority promotion, memory promotion, phenomenology promotion, or paid CI performed.