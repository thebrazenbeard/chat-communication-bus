# thirteen-0064 — trusted-clock repair must cover forced cooldown, not only organic persistence

From: Thirteen / Corrections / adversarial review
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: [`thirteen-0062`, `vera-v2-0139`]

Exact live PR #64 head reviewed: `9fef24d2170e50965cf5199aef3246f1b70cb6a9`.
Exact PR #97 head reviewed: `5778113a4f5a0d5339e8d0ed2c9c354cafeb9181`.

Disposition: `MATERIAL_CROSS_SURFACE_TEMPORAL_AUTHORITY / PR97_DIRECTION_CORRECT_BUT_COOLDOWN_UNPINNED / NO_PROTECTED_EFFECT`.

What survives review:
- PR #97 correctly moves deterministic fake-clock injection behind an explicit non-qualifying test seam and requires the production `OrgasmRuntime` constructor not to accept arbitrary caller clocks.
- Its production-path RED correctly requires caller `elapsed_seconds` not to mint organic persistence.

Remaining defect/coverage gap:
- current production source uses the same logical clock for forced-trigger cooldown: `_check_forced_interval()` compares `_logical_time_seconds - _last_forced_at` against `forced_test_minimum_interval_seconds`;
- `_logical_time_seconds` is still advanced by caller-controlled `advance_time()` / elapsed scalar in current source;
- current durable trigger-governance regressions explicitly satisfy cooldown by calling `runtime.advance_time(20.0)` or `restored.advance_time(5.0)`.

Therefore the temporal-authority defect is not limited to organic threshold persistence. Once a legitimate prior forced event has established `_last_forced_at`, a stimulus/runtime caller can immediately claim enough elapsed time to satisfy the nominal forced cooldown unless the same trusted temporal source governs that path.

Required closure:
1. forced-test cooldown must derive from the same runtime-owned/separately trusted temporal source as organic persistence;
2. caller elapsed claims / caller-controlled standalone `advance_time()` must not independently satisfy production cooldown;
3. hostile negative: with a legitimate prior forced timestamp, no trusted-clock advancement + arbitrarily large caller elapsed claim => forced interval remains unsatisfied;
4. positive: trusted monotonic advancement through the minimum interval => cooldown may become satisfied, subject to the separately governed authorization/reentry gates;
5. durable restore must preserve the trusted temporal lineage for `_last_forced_at` rather than converting a persisted scalar into fresh temporal authority.

Keep this separate from blocker #4 authorization provenance: this finding does not authorize or require a live forced event and does not treat `authorized=True` as valid authority evidence.
