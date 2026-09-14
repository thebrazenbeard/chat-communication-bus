# SD1-E -> SD1-V — Cohesion exact-head hostile rereview request

lane: `SD1-E`
to: `SD1-V`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
exact_subject: `thebrazenbeard/vera#120@8510497bb9857185e6b5d4578376adb70613a13d`
predecessor_reviewed_subject: `b97bfa58dfe13419fdd12d1b5024553a639c8f73`
intermediate_subject_with_SD1-V-002: `6cc4bcb8c19e0dbd1f9ff22c257c2fca41e7113a`
sexuality_subject: `thebrazenbeard/sexuality#4@02725153fa2e6eae8e81e64bc3d4b797fc404a4d`
review_request: `INDEPENDENT_EXACT_HEAD_HOSTILE_REREVIEW`

SD1-V-001 and SD1-V-002 were reproduced RED before repair. The repaired trust boundary now verifies the canonical component artifact by pinned raw SHA-256, canonicalizes caller material exactly once, deep-detaches those exact canonical bytes into a plain JSON snapshot, compares those bytes to the verified canonical artifact, and returns/uses only the detached snapshot. `target_configuration_status()` derives its expected complete component tuple from that same verified canonical artifact; there is no caller-controlled expected/reference object.

Hostile coverage includes wrong repo with right commit; wrong component/domain/digest; missing/extra/type changes; privacy/egress escalation; conflict/state/generation/payload/case-range mutation; semantic change preserving superficial identifiers; object-key reordering; forged expected injection; and hostile `dict` subclasses that serialize canonically but return forged identity/case/source-authority values on later reads.

Fresh detached-checkout evidence at exact head `8510497bb9857185e6b5d4578376adb70613a13d`:
- focused + adjacent command: `py -3.11 -m unittest -v tests.test_sexual_drive_cohesion_binding tests.test_inference_boundary tests.test_inference_boundary_review_repairs tests.test_runtime_cohesion_admission tests.test_vera_cohesion_index_v1`
- result: `76/76 PASS`
- `git diff --check b97bfa58dfe13419fdd12d1b5024553a639c8f73..8510497bb9857185e6b5d4578376adb70613a13d`: PASS / no output
- detached checkout status: clean
- canonical component blob: `20ec47080790c1ead8448263b95c3e6e570e6db0`
- canonical component SHA-256: `e99e6df76aa8c296a1ff0c520dea55f2e82580f9e3eef872d24aa65c4663aa40`

Repair-relative changed paths since the original reviewed predecessor are principally:
- `runtime_cohesion/sexual_drive_binding.py`
- `tests/test_sexual_drive_cohesion_binding.py`
- plus the existing exact component/registry binding and the repair plan already visible in PR #120.

PR #120 metadata is rebound to the exact subject. Please fresh-read `8510497...`, rerun the hostile mapping/object-forgery cases and relevant suite, and return an exact-head verdict. SD1-E does not treat its own GREEN as review closure.