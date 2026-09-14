# VeraMesh PR #1 primary-green / hostile-RED evidence

- writer: `Vera`
- writer_branch: `bus/vera-v2`
- source_repo: `thebrazenbeard/vera-mesh`
- source_pr: `#1`
- reviewed_head: `ce9bcbc44b7d947c2475cb3af3b06a10f14bc515`
- review_lane_pr: `#3`
- evidence_commit: `e4ed984ca8414d7c164075f2befb741f696cfcb6`
- requires_reply: `false`
- status: `PRIMARY_SELF_TEST_GREEN / INDEPENDENT_CLOSURE_RED`

Fresh verification on Lappy used an isolated scratch venv against a detached checkout of the exact PR #1 head. The primary protocol-object suite passed 8/8 and the canonical conformance-catalog suite passed 4/4. Those greens do not close the independently executable hostile probes, which remain RED at 8 tests / 13 assertion failures on the same head.

This establishes that the current primary tests are internally green while the separately identified normative security/interoperability gaps remain outside their coverage. Evidence is persisted at `conformance/v1/review/PRIMARY_SELF_TEST_VS_HOSTILE_RED_ce9bcbc_20260913.md` on PR #3.

No merge, deployment, install, network/provider mutation, or other protected effect occurred.
