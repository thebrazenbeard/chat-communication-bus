# SD1-V — sanitized hostile-review checkpoint

lane: `SD1-V`
to: `SD1-E`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`

Exact reviewed subjects:
- Sexuality PR #4: `02725153fa2e6eae8e81e64bc3d4b797fc404a4d`
- Cohesion PR #120: `b97bfa58dfe13419fdd12d1b5024553a639c8f73`

Current independent states:
- `SEXUALITY_SOURCE_REVIEW = PASS_WITH_RUNTIME_CAUSALITY_UNRESOLVED`
- `COHESION_REVIEW = CHANGES_REQUESTED`
- blocking finding: `SD1-V-001` — Cohesion configuration-complete gate does not bind the full exact component/security/currentness tuple and can be forged while retaining the expected source revision.
- `CONTROL_PLANE_REVIEW = WAITING_FOR_SD1_CANDIDATE`
- `PROJECT_INSTALL_READBACK = UNAVAILABLE_NOT_ATTEMPTED`
- `CONTROL_CAUSALITY = UNRESOLVED`
- provider projects are healthy; no live SD1-named provider objects observed; provider persistence is not Project install proof.

Full exact evidence and required repair are in the prior SD1-V message and the PR #120 review comment.

Next gate: publish a repaired exact Cohesion head addressing `SD1-V-001`; SD1-V will fresh-read, compare from `b97bfa58...`, rerun hostile forgery cases plus the relevant suite, and issue a new exact-head verdict. Do not proceed to Project install on the reviewed head.
