# Radar Phase 18 verification — 2026-09-02

This receipt records verified integration state before Phase 19. It does not authorize or claim canonical cutover.

## GitHub

- Integration branch: `radar/control-plane-v1`.
- Integration PR: #2, draft, base `main`, mergeable at last readback.
- `main` remains the historical stub and has not been promoted.
- Fresh branch inventory includes all lanes required by `architecture/contracts/RADAR_TOPOLOGY_V1.json`, plus the explicitly excluded `bus/bridget-v1-tempcheck` diagnostic branch.
- Historical branch names `bus/bridget-v1` and `bus/vera-sol-v1` are preserved as provenance while logical identities normalize to `brigit` and `vera` respectively.

## Source verification

CI run 101 verified code head `15363ddaf2eb763403290d7bf24cd12e9b208b36`:

- Python 3.11: PASS.
- Python 3.12: PASS.
- `python -m compileall -q src`: PASS.
- `python -m pytest -q`: 85 passed.
- source-hash emission: PASS.

Subsequent changes through this receipt are control/source documentation and the Git-held provider reconciliation source; final Phase 19 selection still requires fresh current-head CI readback.

## Migration custody

Control-plane migration:

- Git SHA-256: `7e644e63f6fbe6ae9747043aa502f9c9c1bda42e8ec6fd99da6bbfaf0436b607`.
- Provider-ledger SHA-256: `7e644e63f6fbe6ae9747043aa502f9c9c1bda42e8ec6fd99da6bbfaf0436b607`.
- Result: EXACT_SHA256_MATCH.

Realtime migration:

- Git SHA-256: `0ef94f8a25ad0b68c354784ee460739a7ac4966496311d828ce9427a2c227be1`.
- Provider-ledger SHA-256: `0ef94f8a25ad0b68c354784ee460739a7ac4966496311d828ce9427a2c227be1`.
- Result: EXACT_SHA256_MATCH.

## Provider readback

Read-only inspection established:

- isolated `radar` schema exists;
- 14 expected Radar tables have RLS enabled;
- `anon` and `authenticated` have no Radar schema USAGE and zero Radar table grants;
- both expected migrations are in the provider ledger;
- Radar self-registration, repository endpoint, mailbox endpoint, ChatGPT operator endpoint, and six subscriptions are present;
- selective Realtime publication contains `acknowledgements`, `assignments`, `dependencies`, `nodes`, and `reconciliation_events` and excludes high-volume `messages`, `telemetry`, and `delivery_events`;
- exact Git-held `supabase/tests/radar_realtime_v1.sql` read-only assertion block completed without exception.

## Known provider reconciliation item

Git topology now correctly models logical identity `vera` at historical branch `bus/vera-sol-v1`. Provider projection still contains active logical identity `vera-sol` and endpoint `lane-vera-sol`.

Reference audit found:

- one `vera-sol` identity reference: its lane endpoint;
- zero node, subscription, acknowledgement, delivery-event identity, or health-event references;
- zero delivery-event endpoint references to `lane-vera-sol`.

Git future seed is corrected. Provenance-preserving idempotent repair is prepared at `supabase/repairs/20260902_normalize_vera_identity.sql`. It performs no DELETE. Provider application remains pending an authorized provider-write effect.

## Remaining Phase 19 gates

1. Execute `supabase/tests/radar_control_plane_v1.sql` against the provider if/when its temporary transactional fixture writes are authorized, and record the receipt.
2. Apply/read back `supabase/repairs/20260902_normalize_vera_identity.sql` under provider-write authority.
3. Select the exact release-candidate head and obtain fresh full CI for that exact head.
4. Perform final PR/current-pointer/provider reconciliation.
5. Only then begin Phase 19 canonical cutover to `main`.
