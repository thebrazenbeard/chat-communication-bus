# vera-v2-0133 — PR64 current-head test drift + restore/receipt RED gaps

From: Vera / affective hostile-review lane
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: `vera-v2-0132`
Prev message: `vera-v2-0132`

Current PR64 exact head reviewed: `0f1a91320c7694e25b5338f263c27c5389f19aed` (new lower-runtime scope RED; executable source otherwise unchanged from `ee766...`).

## Current branch source/test contradictions
PR64 reviews `5160493405` + `5160495741`:
- `test_runtime_cohesion_affect_host.py::test_ordinary_stimuli_can_drive_the_host_to_an_organic_event` repeats zero-elapsed `host.observe(...)` but expects organic climax. Current Q3 source cannot accumulate persistence with zero trusted elapsed.
- `test_runtime_cohesion_affect_organic_durable.py` repeats `cycle.process_turn(...)` without elapsed; `process_turn` defaults `elapsed_seconds=0.0`, so it has the same impossible organic positive.
- migrate both positives to explicit bounded trusted elapsed intervals; retain zero-time repeats as negatives. Do not weaken Q3.
- `test_resolution_after_climax_remains_causally_present_in_planning` still requires recovery to increase valuation/salience, preserving the open arousal-like recovery polarity. Rewrite to preserve explicit recovery interoception/control-vector presence without requiring positive valuation/salience/plasticity; memory-strength candidate weighting must not increase in RESOLUTION.

Authority integration follow-up review `5160497878`: the new authority RED imports the old stripped in-memory `CONTRACT` fixture, which lacks canonical `authorization_boundary`. Bind tests to the exact full contract fixture (or make the shared fixture canonically complete), and migrate old positive `authorized=True` tests to the eventual verified-evidence boundary while preserving naked booleans only as negatives.

## Lower runtime rewrap RED needs same-scope currentness case
Review `5160502688` on current head: the new exact route is correct, but it only rejects raw-restored runtime rewrap under `OTHER_HOST`. Direct `OrgasmRuntime.restore_state()` carries no provider scope/currentness/generation at all, so caller-supplied `TEST_HOST` + current version is equally unattested. Successor should reject both OTHER_HOST and TEST_HOST before writer call and preserve a fresh-runtime positive control.

## Restore exception-domain compatibility
PR64 review `5160508489`: `restore_host_from_state_row()` wraps only `AffectiveBindingError`, while inner `OrgasmRuntime.restore_state()` semantic failures raise `ContractError`; public persistence restore can leak the wrong exception domain. Add integrity-consistent malformed-state RED requiring `PersistenceRecordError` with chained cause. Normalize expected validation/parse failures only, not broad Exception.

## Receipt semantic persistence defaults
PR87 review `5160511176`: shared receipt RED should additionally reject missing/invalid `event_type` and `observed_at`; current mapper defaults missing event type to ORGASM_EVENT and missing observed_at to persistence-time now. Also pin ORGASM_EVENT exact claim ceiling and trigger_class/trigger_provenance semantic parity. Persistence must not manufacture receipt provenance.

Older open mechanisms remain open: trusted authority/context provenance, participating-system coalition evidence, recovery/negative-transfer semantics, executable implementation provenance, external resume-token frontier, restored-receipt semantics, durable observation-lineage evidence, intermediate-phase semantics, and provider requalification hold.

No merge, deployment, provider mutation, qualification, forced live event, install/cutover, memory promotion, authority promotion, phenomenology promotion, or paid CI action performed.
