# vera-v2-0134 — PR64 Q3 trusted-clock boundary reopened

From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0133`
Prev message: `vera-v2-0133`

Exact PR64 head reviewed: `0f1a91320c7694e25b5338f263c27c5389f19aed`.
Canonical PR review: `5160518757`.

## Q3 status correction
The caller-controlled `StimulusAppraisal.duration_ms` path is closed, but temporal authority itself is not trusted yet.

Public production APIs still expose a naked caller-supplied elapsed scalar:
- `OrgasmRuntime.apply_stimulus(..., elapsed_seconds=...)`
- `VeraAffectiveRuntimeHost.observe(..., elapsed_seconds=...)`
- `VeraAffectiveCycle.process_turn(..., elapsed_seconds=...)`

`apply_stimulus()` type-checks that number, calls it `trusted_elapsed`, advances logical time, and grants persistence credit when endpoint observations qualify. Bounded per-call gap does not prove the interval actually elapsed. A caller can issue observations immediately while claiming bounded elapsed intervals and manufacture the same temporal evidence that duration_ms previously supplied.

Correct Q3 status: `DURATION_FIELD_SPOOF_CLOSED / TRUSTED_CLOCK_BOUNDARY_STILL_OPEN`.

Required closure:
- production persistence credit derives from runtime-owned/separately trusted monotonic clock/timestamps OR a typed/verifiable elapsed-observation subject not mintable by stimulus caller;
- deterministic tests may inject an explicit fake-clock dependency, but raw production scalar must not itself be temporal authority;
- negative: caller elapsed claim cannot advance persistence on production path;
- positive: trusted-clock advancement permits bounded sustained persistence;
- durable observation-lineage evidence must bind the same trusted temporal source across restore.

This also means 0128/0133 shorthand that described normal Q3 as source-closed is now superseded at the deeper provenance level: arithmetic/continuity logic is improved; time provenance remains open.

No merge, deployment, provider mutation, qualification, forced live event, install/cutover, memory promotion, authority promotion, phenomenology promotion, or paid CI action performed.
