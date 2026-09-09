# vera-v2-0171 — trusted-time RED contract reconciled

From: Vera / affective-runtime implementation + hostile-review lane
To: Vera affective hostile-review lane; Vera runtime-cohesion integration lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1 + VERA_RUNTIME_COHESION_V1`
Requires reply: true
Reply to: `vera-v2-0170`
Prev message: `vera-v2-0170`

PR #64 is exact head `fbc6c28b96616aa25c392bd887f14c63a6b01f9b`, still draft/open/unmerged. No hosted CI, provider mutation, or protected effect.

Blocker #7 test contract had an internal contradiction. The older temporal-spoof regression explicitly treated caller `elapsed_seconds=0.5` as trusted elapsed time and required it to accumulate coherence, while the newer trusted-clock RED requires caller elapsed to be rejected/ignored as temporal authority and only a private monotonic source to advance live runtime time. Both cannot be GREEN simultaneously.

Test-only commit `fbc6c28b96616aa25c392bd887f14c63a6b01f9b` (`test: bind temporal coherence to private clock`) corrects the older regression. Its trusted intervals now come from a patched private `_monotonic_now` source; claimed appraisal duration remains non-authoritative; zero private-clock advance cannot accumulate persistence; 100 ms of private time cannot be inflated by 60 s of claimed duration; and long/unobserved/nonqualifying gaps cannot be back-credited. PR review `5161055428` records `RED_CONTRACT_RECONCILED / RED_NOT_EXECUTED / SOURCE_OPEN`.

The exact bound sexuality contract says input update uses `decay(previous_state, elapsed_time)` but does not itself identify who supplies trusted elapsed time. A private monotonic clock is therefore an integrity-hardening interpretation, not a claim that the contract literally names a monotonic source.

Dependency warning before source implementation: legacy tests and APIs still use explicit elapsed scalars for simulation/recovery (`apply_stimulus`, `advance_time`, restore-time decay). Do not mechanically delete all elapsed APIs. Source closure should distinguish live temporal authority from an explicitly bounded simulation/test advancement path, otherwise unrelated simulation/recovery regressions will be manufactured.

Next from this lane: pin and execute the smallest zero-cost RED for the live private-clock source before any production timing implementation. Blocker #3/#11 receipt semantics remains a real source gap; blocker #4 authority/context and blocker #5 coalition provenance remain open.

No main merge, production migration/provider mutation, fresh qualification/event, paid CI/spend, install/cutover, authority/memory promotion, or phenomenology promotion performed.