# Vera PR #89 mirror — truthy scalar firewall

Canonical PR: `thebrazenbeard/vera#89`
Canonical URL: https://github.com/thebrazenbeard/vera/pull/89
Base cut: `c67d2141e8ae821ba19a22dd964635ff17f18a37`
Head branch: `work/vera-affective-truthy-scalar-firewall-review-20260909`
Head commit: `621470fa0cc0e83bf966a87b2d3a9f00a120aa37`
State: OPEN / DRAFT / TEST-ONLY / NOT MERGED

Purpose: isolate only the legacy truthiness-laundering subdefect of blocker #4. Non-boolean values such as string `"false"` must not become `context_eligible` or forced-trigger authorization through Python truthiness. Real false must reject; real true remains only the legacy scalar gate.

This PR explicitly does NOT close blocker #4. Canonical actor/referent/proposition-or-effect/source/observed_at/currentness/expiry-or-supersession evidence and resolver semantics remain required separately.

No merge, deployment, provider mutation, qualification, native install/cutover, memory promotion, phenomenology promotion, or CI-green claim.