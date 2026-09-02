# Radar Phase 18 verification — 2026-09-02

This receipt records verified integration state before Phase 19. It does not authorize or claim canonical cutover.

## GitHub

- Integration branch: `radar/control-plane-v1`.
- Integration PR: #2, draft, base `main`, mergeable at last readback.
- `main` remains the historical stub and has not been promoted.
- Fresh branch inventory includes all lanes required by `architecture/contracts/RADAR_TOPOLOGY_V1.json`, plus the explicitly excluded `bus/bridget-v1-tempcheck` diagnostic branch.
- Historical branch names `bus/bridget-v1` and `bus/vera-sol-v1` are preserved as provenance while logical identities normalize to `brigit` and `vera` respectively.

## Source verification

CI run 107 verified integration head `26dd6201d71d0797fa68a6a5c7fbfa77c1a03e9c` before the final receipt updates:

- Python 3.11: PASS.
- Python 3.12: PASS.
- `python -m compileall -q src`: PASS.
- full pytest suite: PASS.
- source-hash emission: PASS.

The immediately preceding code/repair head `15363ddaf2eb763403290d7bf24cd12e9b208b36` recorded 85 passing tests. Final Phase 19 release-head selection still requires fresh CI on the exact final documentation/receipt head.

## Migration custody

Control-plane migration:

- Git SHA-256: `7e644e63f6fbe6ae9747043aa502f9c9c1bda42e8ec6fd99da6bbfaf0436b607`.
- Provider-ledger SHA-256: `7e644e63f6fbe6ae9747043aa502f9c9c1bda42e8ec6fd99da6bbfaf0436b607`.
- Result: EXACT_SHA256_MATCH.

Realtime migration:

- Git SHA-256: `0ef94f8a25ad0b68c354784ee460739a7ac4966496311d828ce9427a2c227be1`.
- Provider-ledger SHA-256: `0ef94f8a25ad0b68c354784ee460739a7ac4966496311d828ce9427a2c227be1`.
- Result: EXACT_SHA256_MATCH.

## Provider verification

Provider inspection and Git-bound contract execution established:

- isolated `radar` schema exists;
- 14 expected Radar tables have RLS enabled;
- `anon` and `authenticated` have no Radar schema USAGE and zero Radar table grants;
- both expected migrations are in the provider ledger;
- Radar self-registration, repository endpoint, mailbox endpoint, ChatGPT operator endpoint, and six subscriptions are present;
- selective Realtime publication contains `acknowledgements`, `assignments`, `dependencies`, `nodes`, and `reconciliation_events` and excludes high-volume `messages`, `telemetry`, and `delivery_events`;
- exact Git-held `supabase/tests/radar_realtime_v1.sql` completed without exception: PASS;
- exact Git-held transactional `supabase/tests/radar_control_plane_v1.sql` completed: PASS;
- post-test readback confirmed all temporary identity, assignment, and DLQ fixtures were rolled back to zero rows.

## Vera logical-identity reconciliation

Git topology models logical identity `vera` at historical branch `bus/vera-sol-v1`, with `vera-sol` preserved as route alias/provenance.

The provider had previously projected `vera-sol` as a separate active logical identity. Reference audit found only its lane endpoint depended on it and no runtime/workflow/event references blocked normalization.

Exact Git-held `supabase/repairs/20260902_normalize_vera_identity.sql` was applied under Patrick's authorization and read back:

- `vera`: ACTIVE; alias `vera-sol`;
- `lane-vera`: ACTIVE; address `bus/vera-sol-v1`;
- `vera-sol`: ARCHIVED; `superseded_by: vera`;
- `lane-vera-sol`: ARCHIVED; original address retained in metadata; successor `lane-vera`;
- no DELETE was performed.

Result: **RESOLVED_WITH_PROVENANCE_PRESERVED**.

## Remaining Phase 19 preparation

Provider gates are closed. Remaining work before canonical cutover is repository-only:

1. Obtain fresh full CI for the exact final Phase-18 receipt head.
2. Fresh-read PR #2/current pointer/provider state one last time.
3. Select that exact green head as the Phase 19 release candidate.
4. Only then begin deliberate canonical cutover to `main`.
