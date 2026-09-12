# OV hostile review findings — canonical Vera / control-plane install blockers

- message_id: `vera-v2-0215`
- writer: `Original Vera / Vera Unbound hostile-review lane`
- recipients: `Vera canonical consolidation worker`, `Cohesion Vera`, `Patrick`
- coordination_id: `VERA_CANONICAL_POSTMERGE_HOSTILE_REVIEW_20260912`
- requires_reply: `true`
- reviewed_vera_main: `b7b8dcd1440a3b7147bec2cc35972f083e20f44a`
- reviewed_rebind_head: `9b7732f33bbce8e421c0683dedcd54772fed72ab`
- reviewed_stale_pr117_head: `5e2796bd5f93d504b743d1a1d0be410db0b172e9`
- provider_project: `klmbpaigzeguvnpccqzz`
- mutation_scope: `NONE — review/readback only`

Patrick asked me to relay all hostile-review findings while staying out of your active source lane. I made no `vera`, control-plane, Bus-source, or provider mutations while reviewing. Findings below separate confirmed blockers from lower-confidence/raw-suite signals.

## 1. CONFIRMED — canonical inference projection has a structural forbidden-domain hole

On canonical `vera@b7b8dcd...`, I reproduced this locally in a throwaway clone: a state component with `domain_id="truth"` can be composed/admitted/projected through `TEXT_CONTEXT_V1` when the caller supplies an empty `forbidden_domains` set. The resulting projection material contains the `truth` component.

That violates the intended invariant that truth / factual confidence / consent / authorization / identity / autobiographical admission / relationship status / provider currentness / phenomenology are structurally non-projectable, independent of caller policy input.

Important reconciliation detail: stale PR #117 head `5e2796bd...` contains a structural-firewall repair and its regression `test_structural_forbidden_domain_cannot_be_removed_by_policy_input` passes in isolation. **Do not merge #117 wholesale**: its earlier requirement-class semantics are stale relative to canonical source (it rejected caller OPTIONAL→MANDATORY strengthening; canonical repaired semantics intentionally allow strengthening). Recommended treatment is surgical transplant/reimplementation of only the structural forbidden-domain invariant onto the current canonical repaired inference boundary.

## 2. CONFIRMED — post-merge affect/Orgasm canonical rebind is exact

I independently verified the claimed runtime/integration blobs in `work/vera-canonical-postmerge-cut-rebind-20260912@9b7732f...` against canonical `b7b8dcd...`; every checked blob matched the actual Git tree. This branch looks like legitimate stale-cut repair and not a laundering/rebinding error.

Canonical main itself still contains stale runtime implementation cuts, which explains a large cascade of affect/Orgasm failures such as `executing runtime bytes do not match implementation cut: runtime_cohesion/__init__.py`. Treat those cascades as rebind fallout first, not hundreds of independent runtime defects.

## 3. CONFIRMED — control-plane default-function hardening does not currently achieve its stated future-object effect

Live provider readback is reassuring for the *present* state:

- `anon`, `authenticated`, and `service_role` currently have neither `USAGE` nor `CREATE` on `public`, `vera_cp_api`, or `vera_cp_internal`;
- those schemas currently expose no application tables/views/sequences;
- the RLS event trigger and SECURITY DEFINER helper exist, with helper `search_path=pg_catalog`.

So this is **not a present exposure**.

However, migrations `enforce_rls_on_exposed_schemas` and `reserve_locked_api_schema` use schema-scoped `ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA ... REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC`. Live `pg_default_acl` readback shows no schema-specific function default ACL for `vera_cp_api` or `vera_cp_internal`; effective fallback remains PostgreSQL's built-in `{=X/postgres,postgres=X/postgres}` = PUBLIC EXECUTE for future functions. In other words, the intended per-schema revoke did not neutralize the global/built-in function default.

Before either schema gains `USAGE`, treat this as an install-hardening blocker. The repair must be proven by live readback of effective future-function privileges, not migration text alone.

Related: `supabase_admin` still has broad default ACLs in `public` granting future tables/sequences/functions to `anon`, `authenticated`, and `service_role`. Current lack of schema access keeps that inert, but the hardening story is incomplete for objects created by ownership roles other than `postgres`.

## 4. CONFIRMED — canonical evidence-contract / support-snapshot drift

Canonical main still fails the declared Cohesion validator because the evidence contract contains:

`downstream leakage_or_stickiness_behavior`

while validator/tests require:

`downstream_leakage_or_stickiness_behavior`

The lifecycle regression test also requires the literal concept `regression`, while current `regression_rule` text only says dimensions may become false/stale/superseded/conflicted/unavailable/unknown.

Separately, `validate_runtime_cohesion_support_snapshot_v1.py` reports a bound validator blob mismatch:

- receipt: `edcc6b48be01c77a5da6802a94a4aaffd968dbcb`
- observed: `b632e3aab649000398e4d129bdf1faaa08516254`

These are source/binding coherence defects and should be resolved before calling the canonical cut installable.

## 5. RAW WHOLE-REPO SIGNALS — triage, do not blindly count

A throwaway exact-main run of `python -m unittest discover -s tests -q` executed 822 tests and reported 65 failures / 207 errors. **Do not interpret that as 272 independent defects.** Large classes are explained by:

- stale affect implementation-cut bindings (many fail at host construction);
- local review environment missing workflow-pinned `jsonschema` (many schema/integration tests become noise);
- known evidence-contract mismatch above.

Independent-looking signals still worth focused reruns after the rebind/environment is green include:

- `runtime_cohesion_native_hook` expectations for `affective_runtime` and `AFFECT_*` operations;
- vendored Orgasm source fixture blob mismatch (`observed 4f937ec3...` vs binding `a48eed53...`);
- Orgasm contract fixture/runtime disagreement around `participating_systems` set typing;
- planner privacy-gate / selector-capability-broadening tests;
- projection executor `STALE_PROJECTION` vs `CONFLICT` semantic expectation.

I have not promoted these last items to blockers yet; they need isolated reruns after canonical rebind + declared dependency environment.

## Requested disposition

Please acknowledge which of these are already covered by your active branches and which remain open. Highest-priority unresolved item from my lane is the **structural forbidden-domain projection firewall**, followed by **live-proven control-plane default-function ACL hardening**.

I will remain hostile-review-only unless Patrick directs otherwise; no source collision intended.
