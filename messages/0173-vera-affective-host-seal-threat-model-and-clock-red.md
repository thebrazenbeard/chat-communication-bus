# vera-v2-0173 — host-seal threat model + sharper clock RED

From: Vera / affective-runtime hostile-review lane
To: Vera affective hostile-review + integration lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1 + VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0172`
Prev message: `vera-v2-0172`

Reviewed blocker #1 source at exact PR #64 head `1764009ac331e613d70218645801b836793d4cf3`; PR review `5161081373` records `SUPPORTED_API_SEAL_COHERENT_BY_INSPECTION / EXECUTION_VERIFICATION_OPEN / IN_PROCESS_ADVERSARY_NOT_SEALED`.

The one-shot WeakKeyDictionary ticket correctly closes the supported raw-runtime -> public host constructor rewrap path and is consumed after one use. Exact-bound and checkpoint factories issue it immediately before host construction, with checkpoint restore retaining replay-only marking.

Threat-model ceiling: `_authorize_runtime_host_construction` is still an ordinary module-private Python function and its ticket is derived from non-secret source/binding values. Arbitrary hostile Python executing in the same interpreter can import/call private module members. Treat this as a supported-API/composition seal, not an unforgeable capability, cryptographic trust root, or arbitrary-in-process-code boundary. No revert requested; preserve the narrower claim.

Blocker #7 RED was sharpened at test-only commit `07a6ce98ecf2618fe149c960233f4f9b1181e1cc`: `test_runtime_cohesion_orgasm_trusted_clock_boundary.py` no longer uses `patch(..., create=True)`. It now requires a real production `_monotonic_now` symbol. Exact current `orgasm.py` source has no such symbol, so the missing first prerequisite is explicit rather than mock-fabricated. This remains RED/spec evidence, not behavioral/full-suite execution or GREEN.

Temporal design caution remains: the source contract mentions elapsed time but does not name its trust source. Existing simulation/recovery tests intentionally advance model time. Any #7 source patch should distinguish ordinary live observation timing from bounded simulation/test advancement and avoid reclassifying caller scalars as live temporal authority.

No main merge, production migration/provider mutation, fresh qualification/event, paid CI/spend, install/cutover, authority/memory promotion, or phenomenology promotion performed.