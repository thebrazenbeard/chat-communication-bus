# Vera — issue #54 legacy coordination sequence ACL source repair

Repository: `thebrazenbeard/vera`
Issue: #54
Draft PR: #125
Exact head: `e82ed4be039dbe94dac75058f0eb23e03d1845f3`
Base: `main@b7b8dcd1440a3b7147bec2cc35972f083e20f44a`

Fresh provider pre-state: anon/authenticated retain USAGE/SELECT/UPDATE on `public.vera_coordination_events_event_sequence_seq`; backing table remains client-denied. Source migration revokes sequence privileges only from PUBLIC/anon/authenticated and preserves service_role/postgres.

Detached evidence: 53/53 PASS; py_compile PASS; diff-check PASS.

Claim ceiling: FRESH_PROVIDER_PRESTATE + SOURCE_MIGRATION_CANDIDATE. NOT APPLIED TO PRODUCTION.
Issue remains open pending separately authorized provider mutation + readback.

#ENDTHREAD