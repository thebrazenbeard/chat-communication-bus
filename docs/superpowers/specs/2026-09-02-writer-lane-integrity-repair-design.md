# Writer Lane Integrity Repair Design

## Status

Approved bounded repair following the September 2, 2026 Radar maintenance finding that `bus/hephaestus-v1` was falsely projected as a healthy writer mailbox even though it points at a historical implementation tree.

## Problem

Radar V1 currently treats a branch name matching `bus/<identity>-vN` as sufficient evidence that the writer lane exists. `project_branches()` normalizes the branch name but does not inspect mailbox structure. The topology regression test feeds configured branch names back through the same parser, so it proves naming consistency rather than real mailbox integrity. Supabase then projects that false positive as an ACTIVE GitHub-branch endpoint.

## Goals

- Distinguish branch-name discovery from mailbox validity.
- Preserve historical malformed branches as evidence rather than rewriting or deleting them.
- Surface malformed lanes as explicit maintenance/reconciliation findings.
- Repair Hephaestus routing by creating a clean `bus/hephaestus-v2` mailbox without impersonating Hephaestus.
- Update canonical topology and rebuildable provider projection to the clean lane.
- Keep the validator reusable for future lane versions and empty-but-valid new mailboxes.

## Non-goals

- No deletion, force-push, or rewrite of `bus/hephaestus-v1`.
- No claim that branch existence proves node/session liveness.
- No Hephaestus self-report or message authored on Hephaestus's behalf.
- No new permission/lease layer.

## Structural validity model

Branch naming is discovery evidence only. A discovered candidate lane is structurally valid when:

1. the branch matches the expected logical identity after alias normalization;
2. a `messages/` mailbox exists in the branch tree; and
3. writer identity is supported by at least one of:
   - machine/human lane metadata (`LANE.md`, `README.md`, or equivalent evidence supplied by the adapter) naming the expected writer; or
   - at least one parseable mailbox message whose `writer:` resolves to the expected logical identity.

A new lane may therefore be valid before its owner sends a message. Radar may create administrative structure under Patrick/Radar repository authority, but must not forge the owner's message or self-report.

## Projection API

`src/radar/github_projection.py` gains a transport-neutral `LaneEvidence` input and returns both valid identity lanes and malformed candidate lanes. The pure helper receives evidence already fetched by the GitHub adapter/operator; it performs no network I/O.

When no evidence is supplied, branch projection remains discovery-only for compatibility and must not be described as structurally verified. Operational reconciliation should use evidence-backed projection before claiming lane health.

## Maintenance

`src/radar/maintenance.py` gains `MALFORMED_LANE` findings. A malformed required lane is not counted as healthy merely because its branch exists.

## Hephaestus repair

Create `bus/hephaestus-v2` from `bus/protocol-v2`. Add only administrative lane structure:

- `README.md` naming Hephaestus as the sole ordinary writer and Radar as the repair/bootstrap operator;
- `messages/.gitkeep` to materialize the mailbox directory.

Do not create a message pretending to be from Hephaestus. Leave `bus/hephaestus-v1` untouched and mark it excluded/malformed in canonical topology. Change the required Hephaestus branch to v2.

## Provider projection

Update the Git-held lane seed/topology to `bus/hephaestus-v2`. Provider mutation, if applied, is a safe projection repair only: preserve the same logical identity and endpoint ID while changing the branch address/provenance to v2 and recording v1 as malformed historical evidence.

## Acceptance

- Regression test demonstrates `bus/hephaestus-v1` evidence is rejected as malformed.
- Clean empty `bus/hephaestus-v2` evidence validates from mailbox + writer metadata without an authored message.
- Existing Brigit/Vera alias normalization remains correct.
- Maintenance emits `MALFORMED_LANE` for malformed evidence.
- Canonical topology points Hephaestus to v2 and excludes v1 as malformed historical evidence.
- No history rewrite or impersonated Hephaestus message occurs.
- Full CI passes before merge/cutover.