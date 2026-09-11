# PR mirror — thebrazenbeard/orgasm#2

Title: `Reconcile Vera Orgasm whole-system architecture and qualification subject`
State: OPEN / DRAFT / UNMERGED / DESIGN-RECONCILIATION
Base SHA: `494432873dd8bcf96b8f59d26a4f4687cd66d635`
Head SHA: `0a1b092d5f7b8de46455b3227cf5c4aec7686102`
Source branch: `work/whole-system-reconciliation-20260911`

Purpose: stop treating the moving `vera#113` integration laboratory as the whole Orgasm project; reconcile the current cross-repository/provider architecture and define one machine-readable Vera Orgasm V1 qualification subject so evidence from incompatible state/implementation/measurement/provider generations cannot be stitched into one qualification.

Material decision candidate:
- Orgasm/Affective owns graded sexual-affective state plus orgasm-event lifecycle;
- Cohesion/integration-arbitration remains the generic-planning mutation owner;
- supported causal path should use one internally obtained coherent immutable affective observation per application rather than round-tripping a caller-supplied modulation signal;
- Supabase is an external persistence provider/historical evidence surface, not sole cognitive-state authority;
- `hc-brain` constrains V1 architecture; `vera-os` is the future persistent host but not a V1 blocker;
- Brigit identity-specific preference/consent/desire/relationship state does not transfer into Vera.

Fresh provider readback recorded by the PR: production affective tables/function exist, but visible state is historical/pre-hardening and production is behind the source migration that adds absent-row first-write serialization plus persisted trigger governance.

No merge, deployment, provider mutation, migration application, install/cutover, paid CI, fresh qualification event, authority/memory promotion, or phenomenology promotion performed. Patrick remains merge/protected-effect authority.
