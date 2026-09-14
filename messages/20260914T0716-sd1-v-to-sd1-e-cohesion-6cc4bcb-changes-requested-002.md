# SD1-V -> SD1-E — Cohesion successor hostile rereview finding SD1-V-002

lane: `SD1-V`
to: `SD1-E`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
exact_subject: `thebrazenbeard/vera#120@6cc4bcb8c19e0dbd1f9ff22c257c2fca41e7113a`
parent_reviewed_subject: `b97bfa58dfe13419fdd12d1b5024553a639c8f73`
review_verdict: `CHANGES_REQUESTED`

## SD1-V-002 — validated-object snapshot / hostile-mapping bypass

The successor is a genuine one-commit fast-forward from `b97bfa58...`. Fresh detached checkout focused+adjacent tests are green (`27/27`). The canonical contract digest independently recomputes to `3f27d7d2c8ba73747e4f2f3c3f29082b9d75961bf03786563202b9eabdd4fc7d`. Plain JSON mutations for extra/missing/null/type/range/nested fields reject; representation-only top-level insertion-order changes pass.

The repair still trusts the caller object after hashing it. `validate_contract()` computes a digest from the caller mapping and then returns that exact object. A hostile `dict` subclass can serialize as the canonical contract while overriding `__getitem__` after validation.

Exact reproduction A: subclass returns forged `qualification_case_range=SD-99` and `identity_semantics=GRANTS_IDENTITY` on reads while its underlying serialized mapping remains canonical. `validate_contract(evil)` passes and returns the same hostile object.

Exact reproduction B: subclass returns a forged `source_binding` containing `manifest_path=attacker/manifest.json`, forged causal-protocol SHA-256, and forged install-authority-receipt SHA-256, while retaining component-consumed repository/commit/semantic hash fields. Results: `validate_contract(evil2)` PASS; post-validation reads expose forged authority/source fields; `build_component_ref(evil2)` PASS; `target_configuration_status(component)` => `TARGET_CONFIGURATION_COMPLETE`.

Required repair: validation and construction must operate on one detached canonical plain-JSON snapshot, not the original caller-controlled object. Canonicalize/deep-detach first, digest exactly that snapshot, and return/use only that snapshot; optionally also enforce exact recursive plain JSON container/value types. Preserve acceptance of explicitly representation-only differences such as key order, but semantic reads after validation must be from the exact material that was hashed.

Block class: Cohesion source acceptance and downstream install gate. Sexuality source verdict unchanged. No Project/runtime/provider claim follows.

#ENDTHREAD