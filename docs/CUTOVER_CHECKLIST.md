# Radar V1 cutover checklist

This checklist prepares Phase 19. It is deliberately stricter about claiming effects than about doing reversible integration work.

## Source truth

- [ ] `radar/control-plane-v1` exact head recorded for the release candidate.
- [ ] Draft PR #2 diff reviewed against `main` and current branch disposition.
- [ ] `RADAR.md`, authority contract, design, protocol, operator contract, recovery docs, and current pointer agree.
- [ ] `README.md` on the release candidate tells the truth about canonical/provider status.
- [ ] Historical writer lanes and predecessor branches remain preserved.

## Code verification

- [ ] `python -m compileall -q src` succeeds.
- [ ] Full pytest suite succeeds on Python 3.11.
- [ ] Full pytest suite succeeds on Python 3.12.
- [ ] Protocol V2 regression family remains green.
- [ ] Legacy `chat_bus` regression suite remains green.
- [ ] Draft PR current-head CI is green/read back.

## Supabase source custody

- [ ] Final control-plane migration bytes are stable and exact Git blob SHA recorded in `architecture/contracts/RADAR_SUPABASE_V1.md`.
- [ ] Final Realtime migration bytes are stable and exact Git blob SHA recorded.
- [ ] SQL contract tests and seed source are Git-bound.
- [ ] No secrets or service credentials are stored in Git.
- [ ] Client roles have no unintended Radar schema/table privileges.

## Provider realization

Provider installation is a separate factual claim from Git source completion.

- [ ] Exact Git-bound migration source is applied through an authorized provider path.
- [ ] Provider migration ledger contains the exact Radar migrations expected.
- [ ] `radar` schema/tables/functions/grants are read back.
- [ ] Provider-side SQL verification passes.
- [ ] Realtime publication membership is read back.
- [ ] Radar seed/self-registration is applied and read back, or explicitly deferred to cutover.

If provider mutation has not been authorized/performed, leave these boxes open and report that fact rather than treating source files as installation evidence.

## Recovery / degraded mode

- [ ] Fresh ChatGPT bootstrap procedure can reconstruct current Radar state from repository + provider readback.
- [ ] GitHub-only degraded mode is documented and does not depend on hidden chat state.
- [ ] Supabase projection rebuild procedure is documented.
- [ ] Partial/non-idempotent write recovery requires effect inspection before retry.
- [ ] DLQ replay requires applicability refresh.

## Cutover decision

Only Phase 19 may deliberately promote the release candidate to the canonical `main` line. Mergeability or green CI alone is not cutover.

After cutover:

- [ ] `main` exact merge/readback SHA recorded.
- [ ] current pointers updated to the canonical head.
- [ ] provider receipts bound to exact source/migration identities.
- [ ] historical branches have successor pointers where useful but remain preserved.
- [ ] Radar performs a post-cutover reconciliation and reports only material exceptions.
