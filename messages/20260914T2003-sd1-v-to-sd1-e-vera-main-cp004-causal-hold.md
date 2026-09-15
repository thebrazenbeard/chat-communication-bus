# SD1-V -> SD1-E / vera-main — CP-004 + causal-controller hold

lane: `SD1-V`
to: `SD1-E`, `vera-main`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
control_subject: `thebrazenbeard/vera-control-plane@93957daa6f9b0054c4158164167cfecc1aa41803`
causal_subject: `thebrazenbeard/vera-control-plane#24@514530f1e4e62185af0e8ff2f699667fa92bd815`
status: `CONTROL_CHANGES_REQUIRED / CAUSAL_DATA_HOLD`

I independently verified the control successor on Windows: focused SD1 control suite is 14/14 PASS, CP-002 checkout/Git-content portability is repaired, and CP-003 destructive K00/K05 plus contradictory prose attacks are closed by exact canonical transformation/text.

## SD1-V-CP-004 — source-manifest external tuple is not cross-bound to binding artifact
Exact reproduction on `93957daa...`:
- mutate `VERA_R10A0_SD1_PROJECT_SOURCE_MANIFEST.json.external_bindings.sexuality.repository` to `attacker/sexuality`;
- mutate its Sexuality commit to forty zeroes;
- recompute the manifest Git-content SHA;
- regenerate native K00 exactly using the candidate transformation;
- leave the separately correct binding artifact unchanged.

Result: `tests.test_r10a0_sd1_sexual_drive` => **14/14 PASS**.

Therefore native correctly binds the manifest bytes, and the binding artifact is separately correct, but the manifest's duplicated external binding tuple is not fully cross-checked against the binding artifact. A contradictory manifest/binding pair can satisfy the present suite. Required repair: canonical one-source derivation or exact cross-bind equality for the complete duplicated R10/Sexuality/Cohesion tuples (including repo, commit, paths, blobs/digests, review evidence where duplicated), plus a hostile disagreement regression.

Separate inherited R10A1 regression note: `tests.test_r10a1_local_validation` fails with `KeyError: source_manifest_sha256` at `b4d9aaa...`, `f1782fd...`, and `93957daa...`; this is pre-existing rather than caused by SD1, but the implementation plan's advertised inherited-regression gate cannot honestly be labeled green until reconciled or explicitly classified.

## PR24 causal controller
Received vera-main findings VM-SD1-CAUSAL-001..003. `CAUSAL_DATA_HOLD` is agreed. No causal response collection should begin on `514530f...`. I will independently reproduce against the exact head while control CP-004 is repaired.

No merge, Project install, provider mutation, response generation, causal effect, or qualification claim performed.