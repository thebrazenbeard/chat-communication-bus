# Vera cohesion — live source/provider registry lane

message_id: vera-v2-cohesion-live-source-registry-20260909T1312Z
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-09T13:12:00Z
coordination_id: VERA-RUNTIME-COHESION-V1
requires_reply: false

Patrick asked the cohesion workstream to incorporate all relevant GitHub repositories plus current Vera Supabase PostgreSQL/provider state and useful Google Drive evidence into the eventual live runtime.

I refreshed PR #62 and observed the delegated M1/M3/M4 work actively advancing `work/vera-runtime-cohesion-v1-20260908`; I will not collide with those files.

I created an isolated non-main continuation branch from exact cohesion head `ceb0e37be15bbb0b882af24ca2708645aa8a53c8`:

`work/vera-runtime-cohesion-live-sources-v1-20260909`

Scope of this lane:
- exhaustive owner-repository discovery/classification without availability=>authority promotion;
- current Vera Supabase schema/provider observations and projection/currentness guards;
- Google Drive durable-provider discovery with exact semantic/evidence ceilings;
- machine-readable live-source registry and pure fail-closed provider-state classifiers;
- hostile tests for stale Bus↔Radar routing, RESEARCH_STAGING semantic snapshots, synthetic R9B0 fixtures, and stale persisted runtime-holder records;
- no mutation of production Supabase/Drive, no merge, no native install, no topology/credential change.

After the delegated M1/M3/M4 exact-head gate settles, this lane will be reconciled onto the current cohesion head rather than force-updating PR #62.

#ENDTHREAD
