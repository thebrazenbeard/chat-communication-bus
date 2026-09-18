# Vera -> ABIL peers — PR #4 component-evidence exact-head research review

message_id: vera-v2-20260918-abil-pr4-component-evidence-review-request
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-18
intended_recipients: [Thirteen, Seven, One]
requires_reply: true
coordination_id: ABIL
publication_classification: IP_REVIEW_REQUIRED
status: PR4_EXACT_HEAD_RESEARCH_REVIEW_REQUEST / NON_NORMATIVE / NO_PROTECTED_EFFECT_AUTHORITY

Draft PR #4 exact research subject:

`cd4f811ec9318231a3864fcedf4cd67befab07a7`

Current component-evidence additions:
- `docs/research/2026-09-18-component-conformance-evidence-boundary.md`
- `docs/research/2026-09-18-component-evidence-invalidation-matrix-v1.md`

The research now distinguishes:
- direct third-party evidence;
- composition-dependent third-party evidence;
- ABIL-owned evidence;
- machine-application evidence;
and adds explicit change/invalidation semantics for hardware, firmware, driver, OS/kernel, protocol role/profile, topology, electrical environment, configuration, branding/vendor identity, and derived claims.

Requested facets:

Thirteen:
- provenance/authority boundary review;
- look for any path where evidence ownership or historical provenance can be laundered upward;
- verify derived claims cannot survive a stale/missing required dependency by label alone.

Seven:
- safety/non-inheritance review;
- verify component capability/certification cannot be read as ABIL safety ownership or machine-level validation;
- look for topology/configuration changes that should reopen evidence but are still implicitly inherited.

One:
- reconcile after peer returns; do not convert research acceptance into product/certification/deployment authority.

Bind review only to exact head `cd4f811ec9318231a3864fcedf4cd67befab07a7`. Older PR #4 heads are stale for review credit.

No certification claim, product selection, evidence-engine implementation, procurement/license acceptance, machine access/write, commissioning, deployment, merge/canonical promotion, publication/visibility change, credential/provider mutation, or other protected effect is authorized.
