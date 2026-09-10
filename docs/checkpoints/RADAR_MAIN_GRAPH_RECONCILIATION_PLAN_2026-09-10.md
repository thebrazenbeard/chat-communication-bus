# Radar canonical-main graph reconciliation plan — 2026-09-10

Status: `SOURCE-ONLY PLAN / NO INTEGRATION EFFECT / NO PROTECTED EFFECT`

This record defines the exact safe shape of a future canonical-history reconciliation. It does not construct the merge commit, move `main`, qualify a new commit, deploy provider state, or authorize any protected/live effect.

## Current immutable inputs at this planning cut

- canonical `main`: `87df9b1372d0f65b5c3ced0296122b2140084024`
- canonical `main` tree: `db73fcc73922447f0f19955c3a494e99030d4dca`
- accepted Anchor-E source-freeze head: `24a7be99e64a41d2e698b60fb2f419c99cdb8492`
- accepted Anchor-E source-freeze tree: `e9b4971aa117fc68c802f7ec95decd558f1bfa10`
- qualified immutable projector cut referenced by Anchor E: `dfd3c639d058dcafaa1167e53ad4bdc152d52cf6`
- qualified projector tree: `8e51a28db92739d2ce103c72194330dc84a7c415`
- common historical parent for `main@87df...` and the qualified Radar line: `b1c0ceb80c6ce895927cd715319257b28124d919`

Fresh readback still shows `main@87df...` as a single-parent aggregate commit whose only parent is `b1c0ceb8...`. The previously recorded ten-path comparison established that every file blob introduced by `87df...` is already present byte-for-byte in the qualified `dfd3...` line. Therefore the unresolved difference is graph ancestry, not missing source payload from `main`.

## Proposed deterministic convergence object

If Patrick separately authorizes construction of a reconciliation candidate, the preferred candidate is a true two-parent commit with:

1. first parent: the then-current reviewed Anchor-E integration head, currently `24a7be99e64a41d2e698b60fb2f419c99cdb8492`;
2. second parent: the then-current canonical `main`, currently `87df9b1372d0f65b5c3ced0296122b2140084024`;
3. result tree: exactly the first-parent Anchor-E tree, currently `e9b4971aa117fc68c802f7ec95decd558f1bfa10`;
4. no replay/cherry-pick of `87df...` content, because its unique payload is already present;
5. a commit message that explicitly classifies the object as an unqualified reconciliation candidate until a new authoritative qualification receipt is admitted.

The candidate tree must remain byte-identical to the reviewed Anchor-E integration tree. A merge result that changes any file bytes is not this deterministic candidate and must be reconciled as a different source proposal.

## Why first-parent ordering matters

The reviewed Anchor-E integration line is the source state whose bytes are intended to survive unchanged. Using it as first parent makes the candidate's content lineage and eventual first-parent audit trail explicit. `main@87df...` is incorporated as the second parent solely to reconcile canonical ancestry. This does not make the candidate canonical and does not transfer any existing qualification receipt.

## Qualification boundary

Even when the candidate tree is byte-identical to `24a7...`, the candidate commit SHA is a new Git object. Existing authoritative qualification remains bound only to `dfd3c639... / 8e51a28d...` and does not transfer to the two-parent reconciliation commit.

Before any candidate could become eligible for canonical integration:

1. construct it only after fresh-reading both intended parents and confirming neither moved unexpectedly;
2. verify both parent SHAs and exact parent order from raw commit metadata;
3. verify the candidate tree equals the intended reviewed Anchor-E tree exactly;
4. verify the ten `87df...` changed paths remain byte-identical in the candidate tree;
5. run the full authoritative `LOCAL_NO_PAID_SERVICES` qualification against the exact candidate commit/tree;
6. validate the external schema-V2 receipt against that same clean exact checkout;
7. obtain independent receipt admission for the candidate exact commit/tree;
8. only then present a separate canonical-merge decision to Patrick.

Qualification of the candidate would qualify that exact candidate object only. It would not itself merge `main`, recover the provider, or authorize activation.

## Hard stop conditions

Stop and redesign before candidate construction if any of these are true:

- `main` is no longer exactly `87df9b1372d0f65b5c3ced0296122b2140084024` and its new delta has not been independently reconciled;
- the intended Anchor-E integration head is no longer exactly the reviewed cut and its changes have not been reviewed;
- `87df...` is no longer the only canonical-main ancestry that needs reconciliation;
- any of the ten previously matched main-only path blobs differs in the intended result tree;
- the candidate tree cannot be exactly preserved without conflict resolution or byte changes;
- the candidate would silently inherit `dfd3...` qualification rather than receive a new exact receipt;
- provider recovery or dispatcher activation is coupled into the graph operation;
- Patrick has not separately authorized construction/integration of the reconciliation object when that protected boundary is reached.

## Relationship to provider recovery

Canonical graph reconciliation and provider recovery are separate axes. Issue #16 may only be recovered through the separately reviewed provider-recovery procedure and separate authorization. A canonical-history candidate must not be treated as permission to apply migrations, deploy/reconfigure Edge, set `RADAR_TRUSTED_PROJECTOR_SHA`, seed cursors, activate the dispatcher, or close the incident.

## Current classification

`MAIN_UNIQUE_PAYLOAD_ALREADY_PRESENT / TWO-PARENT_RECONCILIATION_SHAPE_DEFINED / CANDIDATE_NOT_CONSTRUCTED / NEW_EXACT_QUALIFICATION_REQUIRED / MAIN_UNCHANGED / PROVIDER_UNCHANGED / NO_PROTECTED_EFFECT`
