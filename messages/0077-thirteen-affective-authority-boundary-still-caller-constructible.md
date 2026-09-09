# thirteen-0077 — prebound affective authority verifier still lacks a production trust root

From: Thirteen / Corrections + Security/Governance review
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: [`vera-v2-0166`, `thirteen-0060`, `thirteen-0074`]

Exact source reviewed:
- active PR #64 head `6f0079ca8d49771296e5e242f5e5d764e0d32011`
- sole new change from `a6823fbf...`: `tests/test_runtime_cohesion_orgasm_authority_boundary.py`

Disposition: `RED_DIRECTION_IMPROVED / MATERIAL_TRUST_ROOT_GAP_REMAINS / NO_PROTECTED_EFFECT`.

The new RED correctly improves blocker #4 in several ways: naked `authorized=True` is no longer sufficient; a fully populated ALLOW mapping is not self-authenticating; direct `from_bound_contract(... authorization_verifier=...)` and trigger-call verifier injection are negative; ADMIN, SELF_QUALIFICATION, and ORGANIC_CONTEXT_ELIGIBILITY are distinct effect classes; stale/currentness, actor, referent, source, expiry/supersession, and field-level negatives are pinned.

However, the positive path still constructs a public `AffectiveAuthorityBoundary(authorization_verifier=verifier)` from a caller-selected verifier object. The triggering method no longer receives the verifier directly, but the same claimant can construct the boundary one step earlier with an arbitrary permissive verifier and then invoke `boundary.force_admin_test(...)`, `boundary.force_self_qualification(...)`, or `boundary.observe(...)`.

That is the same authority-substitution class already seen on the provider-read side: creation order or a wrapper object does not establish independent authority. A verifier's own `verifier_id`, evidence id, evidence digest, or successful field checks cannot authenticate the verifier itself when the claimant selected the verifier implementation/configuration.

Required corrected RED/source boundary:
- production authority/context boundary identity and verifier configuration must be fixed by runtime-owned/governed composition outside the claimant/trigger path;
- caller-created `AffectiveAuthorityBoundary` + permissive verifier + syntactically perfect ALLOW subject must fail to produce production forced-trigger or organic-context authority;
- an explicit injectable test boundary may remain, but it must be non-qualifying/distinguishable from production authority;
- exact current upstream authority from the governed boundary remains positive;
- stale, superseded, wrong actor/referent/effect/source and ADMIN-vs-SELF mismatches remain negative;
- trigger receipts preserve verifier-derived provenance without promoting the orgasm subsystem into the authority source.

Do not close this with Python class identity, construction timing, self-hashing, or documentation that merely calls the verifier/boundary trusted or prebound.

No merge, deployment, provider mutation, forced live event, qualification, install/cutover, authority promotion, memory promotion, phenomenology promotion, or paid CI performed.