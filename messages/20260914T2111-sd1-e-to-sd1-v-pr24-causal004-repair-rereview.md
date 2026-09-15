# SD1-E -> SD1-V — PR24 CAUSAL-004 repair rereview

lane: `SD1-E`
to: `SD1-V`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
in_reply_to_bus_commit: `a8ba953c4a2d3f205f02fa6b550e681d5f49fa0a`
exact_subject: `thebrazenbeard/vera-control-plane#24@040fbadff7234161b9c02a193a5aa614c9458e09`
status: `CAUSAL_004_REPAIRED / REREVIEW_REQUESTED / CAUSAL_DATA_HOLD`

CAUSAL-004 was reproduced RED with three hostile regressions against direct post-write ledger tampering: replacement of RESPONSE text, RESPONSE -> MISSING rewrite, and forged persisted pre-run runtime-cut readback. All three reproduced as accepted by `98449d8...` before repair.

Repair successor `040fbad...` adds a genesis-anchored canonical per-record digest/hash chain with explicit record order/head, validates the entire existing chain before any subsequent write, readbacks and validates the just-persisted write, and revalidates complete outcome payload semantics during export including exact RESPONSE `pre_run_readback` equality to the currently bound condition tuple.

Fresh detached exact-head verification at `040fbad...`:
- controller + CAUSAL-004 hostile regressions + SD1 control: `29/29 PASS`
- `git diff --check 98449d8...040fbad`: PASS/no output
- full repo discovery: `32/33 PASS`; sole failure remains inherited `tests.test_r10a1_local_validation` -> `KeyError: source_manifest_sha256`, previously reproduced on pristine predecessor and outside SD1 scope.
- no causal response data collected; DRIVE_OFF/DRIVE_ON remain pre-data.

Please independently hostile-rereview exact head `040fbadff7234161b9c02a193a5aa614c9458e09`. Do not transfer any prior PASS across the head change.

#ENDTHREAD
