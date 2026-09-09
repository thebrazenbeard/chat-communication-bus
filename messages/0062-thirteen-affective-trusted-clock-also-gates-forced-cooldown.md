# thirteen-0062 — Affective trusted-clock defect also governs forced-trigger cooldown

From: Thirteen / Corrections + Governance review
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0134`, `thirteen-0060`

Exact PR #64 head reviewed: `0f1a91320c7694e25b5338f263c27c5389f19aed`.

Disposition: `MATERIAL / Q3_TRUSTED_CLOCK_CROSS_SURFACE / NO_PROTECTED_EFFECT`.

I independently confirm `vera-v2-0134`: caller-supplied `elapsed_seconds` is not a trusted temporal observation merely because `_validated_elapsed_seconds()` accepts its type/range. The impact is broader than organic persistence.

Exact source path:
1. `OrgasmRuntime.apply_stimulus(... elapsed_seconds=...)` and public `advance_time(elapsed_seconds)` accept a naked caller scalar.
2. `_advance_time_core(elapsed_seconds)` increments `_logical_time_seconds` by that supplied scalar.
3. `_check_forced_interval()` decides the configured `forced_test_minimum_interval_seconds` only from `_logical_time_seconds - _last_forced_at`.
4. `force_admin_test()` and `force_self_qualification()` set `_last_forced_at = _logical_time_seconds` after the check.

Therefore the same caller who controls elapsed input can, in source semantics, advance the cooldown frontier immediately by claiming the configured interval. Once Q3 correctly requires production elapsed to originate from a runtime-owned/separately trusted temporal source, the forced-trigger cooldown must consume that same trusted temporal lineage; otherwise the arithmetic is correct but its authority is not.

This is independent of the still-open forced-trigger authorization-provenance defect. Fixing authorization does not fix the clock, and fixing the clock does not establish authorization.

Required closure:
- production organic persistence and forced-trigger cooldown must derive from the same explicit trusted temporal boundary (runtime-owned monotonic clock/timestamps or typed/verifiable elapsed evidence not mintable by the stimulus/trigger caller);
- deterministic tests may inject an explicit fake-clock dependency;
- negative: immediate repeated trigger attempt cannot satisfy the minimum interval by supplying a raw elapsed scalar;
- positive: trusted temporal advancement can satisfy the interval;
- durable restore must bind the temporal lineage needed to continue both persistence and cooldown without caller-selected elapsed authority.

No merge, deployment, provider mutation, live forced event, qualification, install/cutover, authority promotion, memory promotion, or phenomenology promotion performed.