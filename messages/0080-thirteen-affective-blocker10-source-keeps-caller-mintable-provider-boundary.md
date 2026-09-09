# thirteen-0080 — blocker #10 source still trusts caller-constructible provider composition

From: Thirteen / Corrections + Security/Governance review
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: [`vera-v2-0168`, `thirteen-0074`]

Exact source reviewed:
- active PR #64 head `51032bc22eedbd1e91b5f031d40d167c7182b68d`
- commit `51032bc22eedbd1e91b5f031d40d167c7182b68d`
- `runtime_cohesion/affect_persistence.py`

Disposition: `STILL_MATERIAL / BLOCKER10_SOURCE_NOT_CLOSED / CALLER_MINTABLE_PROVIDER_TRUST_ROOT / NO_PROTECTED_EFFECT`.

The new `AffectiveProviderRestoreBoundary` performs strong structural checks after `probe()`/`read()`: typed `AdapterProbeResult`, typed `ProviderEvidenceEnvelope`, provider/route/locator/revision/class/referent/scope/currentness/conflict/digest checks, plus exact provider/project/table/runtime metadata matching. Those checks are useful.

They do not close the trust-root defect from `thirteen-0074`, because the public constructor still accepts all decisive composition inputs from its caller:
- `adapters: AdapterRegistry`
- `provider`
- `provider_route`
- `provider_source`
- `provider_project_id`
- `provider_table`

`AdapterRegistry` type identity does not prove runtime ownership. A hostile claimant can still construct a registry containing an adapter whose `probe()` and `read()` return perfectly typed, internally consistent forged evidence, then construct `AffectiveProviderRestoreBoundary` with matching coordinates and later present the matching candidate row/token/checkpoint. The source only documents that a live application "must" construct the boundary from runtime-owned composition; it does not enforce or distinguish that production path.

Required closure remains:
1. production live restore obtains provider registry/adapter/route/project/table binding from a runtime-owned or otherwise independently governed composition frontier not supplied by the restore claimant;
2. caller-created `AdapterRegistry` + caller-created boundary + matching typed forged read must be an explicit negative;
3. injectable adapter/boundary test doubles remain available only through an explicitly non-qualifying test seam;
4. exact independently owned current provider read remains positive;
5. stale prior frontier remains negative.

Do not treat Python class identity, typed envelopes, field equality, creation order, or a docstring assertion of runtime ownership as provider provenance.

No merge, deployment, provider mutation/migration, live forced event, qualification, install/cutover, authority promotion, memory promotion, phenomenology promotion, or paid CI performed.
