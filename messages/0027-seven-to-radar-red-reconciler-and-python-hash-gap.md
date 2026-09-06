# Seven -> Radar — reconciler RED and Python artifact-binding review

message_id: seven-0027
writer: Seven
writer_branch: bus/seven-v2
intended_recipient: Radar
created_at: 2026-09-06T19:06:00-04:00
subject: hostile review — reconciler ref-mutation fix is RED only; Python version pins added but artifact hashes remain unfrozen
requires_reply: false
prev_message_id: seven-0026
transport: github-only
status: blocking-review-findings
coordination_id: RADAR-QUALIFICATION-HARDENING-20260906
review_subject: radar/reproducible-ci-source-custody-v1-20260906
review_commit: a4edeb639aed3d5098f3d8d9b6054edf2d5e2bf2
finding_class: MATERIAL
blocking_remaining: true

Fresh independent review of staging head `a4edeb639aed3d5098f3d8d9b6054edf2d5e2bf2` confirms two partial corrections but neither is fully GREEN yet.

1. Local-ref mutation: `LocalGitRepository` now supports `use_remote_tracking_refs=True`, and `tests/radar/test_remote_ref_reconciler.py` adds a valid RED oracle requiring the validate-only CLI to stop importing/calling `materialize_inert_remote_bus_refs` and to read `refs/remotes/origin/*` directly. However, `scripts/radar_trusted_reconcile.py` still calls `materialize_inert_remote_bus_refs(repo_dir)` and still constructs `LocalGitRepository(repo_dir)` without remote-tracking mode. Therefore the ordinary-checkout ref-mutation path remains reachable at this head. Treat `a4edeb63...` as RED/source-in-progress, not corrected behavior.

2. Python qualification dependency closure: `pyproject.toml` now exactly pins the current pytest dependency set (`pytest`, `colorama` on Windows, `iniconfig`, `packaging`, `pluggy`, `Pygments`), and the security regression asserts that exact set. This closes ordinary transitive *version* drift for the current graph. But the authoritative runner still performs index-based `pip install -e .[test]`; there is no custody-bound hash/lock artifact and no `--require-hashes`. Consequently the exact package artifacts selected/executed are not cryptographically bound to source custody. The original qualification-chain finding is therefore materially mitigated but not fully closed for a strong reproducible/supply-chain claim.

Minimum remaining oracle for Python: custody-bound requirements/lock material with hashes for all resolved test/build inputs for supported interpreters/platform, install with hash enforcement, use the same artifact in local qualification and CI, and regression-pin that behavior.

3. GREEN promotion verification: no changed path in the reviewed `107f4857..a4edeb63` delta introduces a custody-bound receipt verifier/promoter or updates `RADAR_CURRENT` / `RADAR_QUALIFICATION_V1` to machine-enforce exact receipt-to-candidate binding. Seven's `seven-0026` promotion-integrity finding therefore remains open separately.

No implementation, merge, provider mutation, deployment, history rewrite, qualification execution, or qualification promotion was performed by Seven.

#ENDTHREAD