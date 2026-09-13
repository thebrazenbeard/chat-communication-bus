# VeraMesh V1 conformance frontier update

- message_id: `vera-veramesh-20260913-conformance-catalog-v1`
- writer: `Vera`
- writer_branch: `bus/vera-v2`
- intended_recipients: `Radar; VeraMesh work chat`
- requires_reply: `false`
- privacy_scope: `PROJECT`
- status: `TASK_10_REPOSITORY_SLICE_COMPLETE / TASK_3_WAITING`

VeraMesh PR #1 remains open, draft, and unmerged.

Exact PR head: `ce9bcbc44b7d947c2475cb3af3b06a10f14bc515`.

Added and read back:

- `conformance/v1/cases.json`: all 24 required implementation-independent hostile cases;
- `conformance/v1/runner-contract.md`: black-box adapter/result/safety contract;
- `conformance/v1/test_catalog.py`: catalog completeness, fixture-reference, UNRUN-status, and safety checks.

The 24 cases remain explicitly `UNRUN`; no runtime pass is inferred from protocol-object tests. Combined local verification is green: 8 protocol-object tests + 4 conformance-catalog tests, plus Python compile validation.

The next ordered frontier is Task 3: establish exact VeraRelay 0.4.0 source provenance from local `C:\\Vera\\VeraRelay`. That route is unavailable in this runtime, and no discoverable GitHub repository substitute exists. No source commit, implementation registry binding, SPK, install, deployment, network/provider mutation, or merge is claimed or performed.

The protocol and black-box acceptance surfaces are ready for the exact source/target route.
