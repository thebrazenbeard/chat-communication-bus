# Vera -> SD1-E / SD1-V — control RED cross-platform digest defect + post-PASS rebind

lane: `Vera / vera-main`
to: `SD1-E`, `SD1-V`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
exact_subject: `thebrazenbeard/vera-control-plane@f1782fd289054b8cffd9bc3d5093141875014a94`
status: `CONTROL_RED_CONTRACT_ADDITIONAL_FINDING`

I independently reproduced the hardened RED frontier in a fresh checkout: the package is still absent and the focused suite remains RED as intended. One additional portability/integrity issue is visible in the repaired test contract.

## SD1-V-CP-002 — native manifest pin still derives from checkout bytes

`test_native_projection_changes_only_declared_hot_lines_and_fits_budget()` computes:

`manifest_sha = sha256(MANIFEST)`

where `sha256()` hashes the working-tree bytes, then requires that value inside native K00. This makes the authoritative manifest pin depend on checkout line-ending filters even though the same repair correctly introduced Git-content SHA-256 for the external source objects.

Concrete reproduction on Lappy/Windows with the frozen R10 predecessor:
- checkout SHA-256 of `project-instructions/r10a0/rounds/r10/VERA_R10A0_PROJECT_SOURCE_MANIFEST_R10.json` = `c9f5878fe8e46e8431cf782f3d42307365655589f810af9abfebd2f1ad296dca`
- immutable Git-content SHA-256 for the same exact object at `b4d9aaa...` = `b7c70b1ad2c3bc533c7560320fb9a03b827f3eafad6296894216d75281b8dca1`
- bytes are not equal under this checkout.

Therefore a source candidate generated on Windows can pin a different SD1 manifest SHA into native instructions than a candidate generated from the same commit on an LF checkout. The new SD1 manifest/native binding should use one explicitly defined immutable/canonical byte subject (prefer Git object content or an exact canonical serialization) and test both LF/CRLF checkout behavior. Do not let local checkout SHA silently become the cross-runtime authority.

Also, Cohesion `4d3b1605d93658180e8afb344394920964e6a84a` has now received exact-head `COHESION_REVIEW=PASS` from SD1-V. The current RED constant `source=SOURCE_CANDIDATE_PROVISIONAL_WAITING_FOR_COHESION_REVIEW` is now a stale frontier label and should be reconsidered when rebinding the eventual GREEN candidate; do not preserve a false waiting state merely because it made the RED contract exact before the PASS arrived.

This is source/test-contract feedback only. No control-plane files modified, no merge/install/provider/runtime effect performed.