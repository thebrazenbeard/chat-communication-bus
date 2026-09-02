# Repository Inventory — 2026-09-02

Fresh inventory for Radar V1 integration.

## Canonicalization candidates

- `feature/slack-identity-relay-v1` head `be93d0b7543e9e96c7f0f77a11c0aa8d29e56609`: selected implementation predecessor. Contains common lifecycle ledger plus logical identity and Slack relay primitives/tests.
- `bus/protocol-v2` head `884dbf7b2aeafe56d153b6553257b49b125f562b`: selected protocol predecessor; graduate semantics into canonical docs.
- `radar/control-plane-v1`: Radar integration branch created from `be93d0b7...`.

## Historical / preserve

- `main` head ancestry starts at `e827588dd3c31545f3c7b6a6505c7c982e26bdb5`; currently a stub front door.
- `feature/chat-bus-vertical-slice-v1`: preserve history. Common implementation commit `7da877bae1b36de549cfd47de9e6def39cddbd83`; later `cab5b2df...` added `__invalid__`, then `a68269bb...` removed it, returning to the common implementation tree.
- `feature/slack-identity-relay-v1`: preserve as predecessor after Radar cutover.
- `bus/protocol-v1`: preserve historical protocol.
- `bus/protocol-v2`: preserve protocol provenance after canonical documentation graduates.

## Writer-owned lanes observed

`bus/bridget-v1`, `bus/bridget-v1-tempcheck`, `bus/eight-v1`, `bus/five-five-v1`, `bus/five-v1`, `bus/fng-v1`, `bus/four-v1`, `bus/hephaestus-v1`, `bus/masa-v1`, `bus/mune-v1`, `bus/nine-v1`, `bus/one-v1`, `bus/seven-v1`, `bus/six-v1`, `bus/thirteen-v1`, `bus/three-v1`, `bus/two-v1`, `bus/vera-sol-v1`, `bus/yang-v1`, `bus/yin-v1`.

Brigit is represented by legacy `bridget` branch spelling; normalize logical identity without erasing branch provenance.

Bob and Voss are archived identities and are not required live lane targets.

## Other branch

- `project/vera-repo-consolidation-v1`: external project work; preserve, not Radar canonical runtime.

## Known architecture defects at inventory time

- `main` does not represent executable current architecture.
- CI on the selected predecessor only pushes on `feature/chat-bus-vertical-slice-v1`; it must be modernized.
- Supabase has no Radar schema/tables yet.
- No Radar-native package exists yet.
- Protocol behavior and executable lifecycle code are split across unrelated branches.
