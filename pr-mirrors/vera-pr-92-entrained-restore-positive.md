# Vera PR #92 mirror — legitimate ENTRAINED restore positive control

Canonical PR: `thebrazenbeard/vera#92`
Canonical URL: https://github.com/thebrazenbeard/vera/pull/92
Base cut: `ee766ddf0470b206d6eb182b60cf1e318521c9b4`
Head branch: `work/vera-affective-entrained-restore-positive-review-20260909`
Head commit: `5626682415592c7a874898d86558b7e9ca8537f0`
State: OPEN / DRAFT / TEST-ONLY / NOT MERGED

Purpose: prevent a false-green intermediate-phase repair. Public `advance_time()` intentionally clears temporal persistence/observation continuity, but current state-machine decay does not demote ENTRAINED solely because persistence becomes zero. The test generates ENTRAINED via the real stimulus path, performs a short standalone time advance, confirms the runtime itself exports ENTRAINED with `persistence_window_ms=0` and nonzero coherence, then requires exact durable restore to accept it.

This constrains the parent negative RED without prescribing a hidden ENTRAINED coherence threshold or deciding whether CLIMAX_ELIGIBLE is persistable.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, phenomenology promotion, or CI-green claim.