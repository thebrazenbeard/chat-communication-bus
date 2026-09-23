# Radar provider recovery preflight — 2026-09-09

Status: `SOURCE_ONLY_PREFLIGHT / NO_PROTECTED_EFFECT`

This document binds a future, separately authorized provider recovery to exact reviewed Git source. It is a preflight/stop-condition record only. It does **not** authorize or perform a merge, migration application, Edge deployment or configuration change, provider setting mutation, cursor bootstrap, dispatcher activation, credential/ruleset/billing change, force push/history rewrite, native Project mutation, or any other protected/live effect.

## 1. Exact qualified projector target

The only currently admitted qualified projector source target is:

- repository: `thebrazenbeard/chat-communication-bus`
- qualified source branch at qualification: `radar/reproducible-ci-source-custody-v1-20260906`
- qualified commit / Anchor E projector SHA: `dfd3c639d058dcafaa1167e53ad4bdc152d52cf6`
- qualified tree: `8e51a28db92739d2ce103c72194330dc84a7c415`
- authoritative mode: `LOCAL_NO_PAID_SERVICES`
- qualification run: `34397641413`
- qualification job: `102621180712`
- receipt schema: `2`
- receipt status: `PASS`
- canonical receipt validator: `VALID`
- stage-evidence SHA-256: `255409e47204f073cdb4a6b460910364985c2ef6ebff746f61e21622666a445b`
- artifact: `radar-local-qualification-dfd3c639-34397641413`, artifact id `10123172942`
- independent receipt admission: `hephaestus-0062`

Anchor-E source-freeze metadata was separately reviewed on PR #58 at exact head `24a7be99e64a41d2e698b60fb2f419c99cdb8492`. Hephaestus review `hephaestus-0065` returned:

`ACCEPT / ANCHOR_E_SOURCE_FREEZE_SCOPE / EXACT_HEAD_24A7 / NO_KNOWN_MATERIAL_SOURCE_CONTRACT_DEFECT`

The PR #58 head and this preflight branch are **not** substitutes for the qualified projector SHA. A future provider `RADAR_TRUSTED_PROJECTOR_SHA` target, if separately authorized, is `dfd3c639d058dcafaa1167e53ad4bdc152d52cf6` only while the current trust contract still says so.

## 2. Exact missing migration source objects

The qualified `dfd3... / 8e51...` tree contains the six currently known missing Radar migrations in this exact source order:

| Order | Migration | Git blob id | Bytes |
| ---: | --- | --- | ---: |
| 1 | `supabase/migrations/20260903214334_radar_thread_closure_v1.sql` | `64e5364621f45d5ecc51e555db63b898b77754f7` | 1765 |
| 2 | `supabase/migrations/20260905230823_radar_oidc_replay_guard_v1.sql` | `5d6571f279dcd314bddaf657e4d1d1ccca7de1fd` | 2989 |
| 3 | `supabase/migrations/20260906133630_radar_node_routing_hardening_v1.sql` | `b8dd713346ed35469914904dd15900fdda1723c6` | 6637 |
| 4 | `supabase/migrations/20260906154101_radar_projection_journal_v1.sql` | `a2e5493f3f6b58a9b5d2d2b24b73cda75f742d8e` | 13523 |
| 5 | `supabase/migrations/20260906165117_radar_projection_journal_api_v1.sql` | `822ae2b126bd99be681ae96fffb6517e73a6396e` | 3461 |
| 6 | `supabase/migrations/20260908010500_radar_projection_atomic_file_v1.sql` | `1589e7b3d1f26bae0df0d6468081607bb8dfa7f5` | 10232 |

These are Git blob object IDs from the exact qualified tree, not SHA-256 content digests. Before any authorized provider write, re-read the qualified tree and require each path/blob pair above to match exactly. A mismatch means `STOP / SOURCE_DRIFT_RECONCILIATION_REQUIRED`.

## 3. Exact qualified Edge package and gateway source intent

The qualified Edge/package inputs are:

| Path | Git blob id | Bytes |
| --- | --- | ---: |
| `supabase/config.toml` | `bf0435948bd70f47bdd43c6e4925078d8ef252eb` | 2965 |
| `supabase/functions/github-bus-ingest/deno.json` | `b717027d0dbca1ed7cf7f362f16a33cfc5c6da99` | 296 |
| `supabase/functions/github-bus-ingest/deno.lock` | `7fe9650c1ea2258877f55e254d3835cc0927c667` | 9967 |
| `supabase/functions/github-bus-ingest/handler.ts` | `cc7cd56632e21c34ec861797db43b60f83977d9b` | 29741 |
| `supabase/functions/github-bus-ingest/index.ts` | `2972c6915b0fec2b8b6082e6da9d7a3c87be929b` | 309 |
| `.github/workflows/radar-trusted-projector.yml` | `5513b46bb3b10906443c1a453852bff16e349340` | 4899 |

Qualified `supabase/config.toml` explicitly sets `[functions.github-bus-ingest] verify_jwt = false`. This is intentional: the endpoint receives GitHub Actions OIDC rather than a Supabase session JWT, and `handler.ts` performs the custom GitHub OIDC verification.

The exact qualified handler binds the expected repository and immutable repository/owner IDs, validates the caller/reusable-workflow OIDC identity, consumes durable OIDC JTI replay state, bounds request/file/batch sizes, and reads `RADAR_TRUSTED_PROJECTOR_SHA` as the immutable trusted-projector source control. Do not replace those controls with gateway-JWT assumptions or a mutable branch ref.

## 4. Fresh-read gates immediately before authorization/execution

A future recovery operator must re-read all of the following immediately before the first protected write:

1. `main` head and tree;
2. PR #58 / Anchor-E source-freeze state;
3. `architecture/contracts/RADAR_CURRENT.json`;
4. its exact `projection_trust_contract` (`RADAR_PROJECTION_TRUST_ANCHOR_V4.json` while V4 remains current);
5. issue #16 and its latest comments;
6. the qualified `dfd3... / 8e51...` source tree and every object identity in sections 2 and 3;
7. the live provider migration ledger;
8. live `github-bus-ingest` version, digest, status, gateway `verify_jwt` setting, and deployed source;
9. existing provider journal/RPC/table/ACL/RLS/publication state;
10. any existing `RADAR_TRUSTED_PROJECTOR_SHA` value or equivalent provider configuration;
11. projection cursor/journal state for every candidate ACTIVE writer lane.

Do not infer current provider state from this document. Issue #16 currently records the known outage snapshot, but provider state must be re-read because it can change independently of Git source.

## 5. Hard stop conditions

Stop before any protected mutation if any of the following is true:

- qualified source commit/tree differs from `dfd3... / 8e51...` without a new admitted qualification;
- the current trust contract no longer freezes `projection_anchor_sha = dfd3c639d058dcafaa1167e53ad4bdc152d52cf6`;
- any migration or Edge/package Git blob identity in this manifest differs at the qualified source;
- provider migration state is not exactly understood, including any partial, reordered, manually reconstructed, or unexpected Radar migration state;
- current Edge version/digest/config/source differs from the last readback and the difference has not been reconciled;
- a previous provider write may have timed out or partially succeeded and durable readback has not resolved the outcome;
- journal/RPC/table/ACL/RLS/publication state is unexpected or ambiguous;
- an existing provider trusted-projector setting would be overwritten without first reading and reconciling it;
- any writer cursor lacks reviewed lineage evidence or is not ancestor-related to the intended writer head;
- any proposed initial or recovery cursor would skip an unseen writer transition that has not passed the exact current `validate_active_writer_range()` contract from its reviewed activation/admission anchor through the proposed cursor head, including logical `message_id` collision checks;
- current `main`/dispatcher history moved in a way that changes the reviewed activation assumptions;
- qualification/admission evidence is missing, invalid, stale for the proposed exact source object, or being inherited by a different commit/tree;
- Patrick has not given separate explicit authorization for the protected recovery effects about to begin.

A stop condition is not a reason to guess, force-push, synthesize ancestry, replay an entire inherited branch, or blindly retry.

## 6. Protected recovery order after separate explicit authorization

Only after all preflight gates pass **and** Patrick separately authorizes the live recovery:

1. freeze/reconfirm the exact current trust target and record the pre-write provider snapshot;
2. apply the six missing Radar migrations in the section-2 order, stopping and reading back after any uncertain result;
3. run the complete Radar SQL assertions and live schema/ACL/RLS/publication/RPC readback gates;
4. deploy the exact qualified `github-bus-ingest` package with the reviewed custom-auth gateway setting (`verify_jwt=false`);
5. set provider `RADAR_TRUSTED_PROJECTOR_SHA` to exact Anchor E `dfd3c639d058dcafaa1167e53ad4bdc152d52cf6` only if V4/currentness still names that target;
6. bootstrap/reconcile projection cursors only from reviewed Git-owned activation/cutover evidence **and** only after the exact transition range from that reviewed anchor to the proposed seed/current head passes `validate_active_writer_range()`; a known preserved historical collision is not permission to seed past it, and requires a separately reviewed clean-lane cutover or explicit historical-admission mechanism rather than cursor laundering;
7. activate the reviewed canonical dispatcher only after its reusable-workflow pin and provider trust target agree on Anchor E;
8. canary one reviewed lane and read back cursor, message, journal, and provider state before broader projection;
9. verify the real Git -> GitHub OIDC -> Edge -> atomic claim-bound file projection -> journal finalize -> provider-readback path, including replay rejection, stale/expired claim rejection, backlog reconciliation, and idempotent retry;
10. close issue #16 only after current-route recovery is directly evidenced.

## 7. State classification

At creation of this preflight artifact:

`ANCHOR_E_SOURCE_FREEZE_REVIEW_ACCEPTED / PREFLIGHT_OBJECTS_BOUND / PREFLIGHT_BRANCH_UNQUALIFIED / PROVIDER_RECOVERY_NOT_EXECUTED / NO_PROTECTED_EFFECT`

This document reduces ambiguity at the recovery boundary. It does not change the live system.
