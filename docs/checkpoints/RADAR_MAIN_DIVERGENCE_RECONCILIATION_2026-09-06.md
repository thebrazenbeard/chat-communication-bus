# Radar main/staging divergence reconciliation — 2026-09-06

Status: `SOURCE EVIDENCE / HISTORY-ONLY MAIN DELTA VERIFIED / NO INTEGRATION EFFECT`.

This checkpoint records a read-only reconciliation of canonical `main` and the consolidated Radar staging branch. It does not authorize or perform merge, rebase, cherry-pick, force push, history rewrite, provider deployment, migration application, cursor seeding, dispatcher activation, or another protected/live effect.

## Compared refs

- canonical `main`: `87df9b1372d0f65b5c3ced0296122b2140084024`, tree `db73fcc73922447f0f19955c3a494e99030d4dca`
- staging evidence head: `91b4a3a15c6f6a7405a60b276b987fdeb0b2f57f`, tree `520f5bdde2ae89228e9c87cb33f39492124e7ca0`
- merge base: `b1c0ceb80c6ce895927cd715319257b28124d919`
- compare state at that snapshot: `diverged`, staging `ahead_by=106`, `behind_by=1`

The one commit reachable from `main` but not from the staging ancestry is `87df9b1372d0f65b5c3ced0296122b2140084024`, the bundled integration of PRs #28, #29, and #30:

- atomic routing eligibility snapshot hardening;
- canonical Radar V1 duplicate-suppression semantics;
- legacy Slack relay concurrency hardening.

## Main-only commit path reconciliation

The main-only commit changes exactly ten paths. Every one of those ten paths is present on the staging evidence head with the same Git blob SHA, proving byte identity for the complete source/test payload of the main-only commit.

| Path | Main blob | Staging blob | Result |
| --- | --- | --- | --- |
| `docs/protocol/RADAR_DEDUPE_V1.md` | `3b00994fc95a4cb95f49aa7d63a0b167632699d4` | `3b00994fc95a4cb95f49aa7d63a0b167632699d4` | IDENTICAL |
| `src/chat_bus/slack_relay.py` | `1d69d51a4580a49f020fcb1314d6ad83d485605f` | `1d69d51a4580a49f020fcb1314d6ad83d485605f` | IDENTICAL |
| `src/radar/registry.py` | `9929b9d6bf7e9abac58131d0f9aff075a2d82247` | `9929b9d6bf7e9abac58131d0f9aff075a2d82247` | IDENTICAL |
| `src/radar/routing.py` | `b871234677c839ff00b36ea77a498e4903444558` | `b871234677c839ff00b36ea77a498e4903444558` | IDENTICAL |
| `src/radar/runtime.py` | `6c2640fd5e40249fdebf76ca5b45e9b18e7c08f4` | `6c2640fd5e40249fdebf76ca5b45e9b18e7c08f4` | IDENTICAL |
| `tests/chat_bus/test_slack_relay_concurrency.py` | `53bf4f134a66c764e2e4866c0145721b1790593d` | `53bf4f134a66c764e2e4866c0145721b1790593d` | IDENTICAL |
| `tests/radar/test_canonical_dedupe_contract.py` | `a615fe3811200aae29d04e610efab1e411efc754` | `a615fe3811200aae29d04e610efab1e411efc754` | IDENTICAL |
| `tests/radar/test_multi_audience_routing_snapshot.py` | `dd39f12e38abe7146a2f2fac8f6942280a00ce8d` | `dd39f12e38abe7146a2f2fac8f6942280a00ce8d` | IDENTICAL |
| `tests/radar/test_runtime_accounting_contract.py` | `588710d7f025af170c8333242b770218b10b9a2c` | `588710d7f025af170c8333242b770218b10b9a2c` | IDENTICAL |
| `tests/radar/test_runtime_pipeline.py` | `206ada156a06d3a72367a4bedc277c3aeeabbdf7` | `206ada156a06d3a72367a4bedc277c3aeeabbdf7` | IDENTICAL |

## Conclusion

The `behind_by=1` state does not represent a missing source or test delta on staging. The complete content introduced by the main-only PR #28/#29/#30 integration commit is already preserved byte-for-byte on the staging evidence head through its independent lineage.

Therefore:

1. Do not replay/cherry-pick `87df9b1372d0f65b5c3ced0296122b2140084024` merely to recover code; there is no missing code from that commit at the verified snapshot.
2. Treat the one-commit behind count as an ancestry/topology distinction until an authorized integration strategy deliberately reconciles histories.
3. Any eventual integration to canonical `main` still requires Patrick's explicit authorization and must be based on a fresh comparison because either branch may move after this checkpoint.
4. This evidence does not make staging GREEN. Authoritative executable qualification remains the local/no-paid path defined by `architecture/contracts/RADAR_QUALIFICATION_V1.json`.
5. Provider/live issue #16 and all protected recovery effects remain unchanged and unauthorized by this checkpoint.
