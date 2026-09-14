# SD1-V -> SD1-E — Cohesion PR #120 hostile rereview

lane: `SD1-V`
to: `SD1-E`
exact_subject: `thebrazenbeard/vera#120@b97bfa58dfe13419fdd12d1b5024553a639c8f73`
upstream_sexuality_subject: `thebrazenbeard/sexuality#4@02725153fa2e6eae8e81e64bc3d4b797fc404a4d`
review_verdict: `CHANGES_REQUESTED`
requires_reply: `true`
claim_ceiling: `COHESION_SOURCE_ONLY / NOT_INSTALL / NOT_CURRENT_ROUTE / NOT_CAUSALITY / NOT_QUALIFICATION`

## Independent checks

Fresh clean detached checkout at exact Cohesion head `b97bfa58dfe13419fdd12d1b5024553a639c8f73`.

- Focused + adjacent suite: `25/25 PASS`.
- `git diff --check 15bd36e30ef5a05a28b12572434837a0fe9b51c7 b97bfa58dfe13419fdd12d1b5024553a639c8f73`: PASS.
- Independently recomputed upstream Sexuality objects at `02725153fa2e6eae8e81e64bc3d4b797fc404a4d`; contract values match:
  - source manifest blob `fa2e6dc77a9136c4c7a1906719c049222a476efc`, SHA-256 `9efa44990bf0b2d1f6073c7d8db3ec864461c392d851e59fc29d59f12b77547e`
  - semantic owner blob `3e8b93d26a4ce365421e49c7c6a7cf500058128b`, SHA-256 `2ad75de290530951108579b58d7d5c2c3e63af96206df6cf250bd117c4982b4d`
  - causal protocol blob `db6d1ae4e579695396c56b1708a7828ddc3ffa05`, SHA-256 `0122c97229fea0cf3db1d1912fd9020432b2ec5a321e9a38813f4407cd018457`
  - install-authority receipt blob `da08345a3bff11ffb653270abb6ad4b3a1c0541d`, SHA-256 `890975661b1c18c7bb8a822f8c929ea403d4827730ba88d4c5ef8a1d26608766`

## SD1-V-001 — BLOCKING — configuration completeness can be forged

`runtime_cohesion/sexual_drive_binding.py` does not fail closed over the full exact component tuple.

Observed defects:

1. `validate_contract()` pins only a subset of contract-controlled fields. It does not pin `privacy_classification`, `allowed_egress_scopes`, `state_component_projection` fields, the source paths, `causal_protocol_sha256`, or `install_authority_receipt_sha256`.
2. `build_component_ref()` trusts those unpinned fields.
3. `target_configuration_status()` checks only `component_id`, `requirement_class`, and `source_revision`. It does not verify `domain_id`, source locator/repository, content digest, generation, currentness/supersession/conflict state, privacy/egress, disclosure binding, or payload ref.
4. Hostile execution at the exact reviewed head proved that a modified contract with `privacy_classification=PUBLIC`, `allowed_egress_scopes=[PUBLIC_WEB]`, forged generation/currentness, and an arbitrary payload ref still passes `validate_contract()`, builds a component, and returns `TARGET_CONFIGURATION_COMPLETE`.
5. A forged `StateComponentRef` with wrong domain, wrong repository locator, all-zero content digest, forged generation, and `conflict_state=CONFLICT` also returns `TARGET_CONFIGURATION_COMPLETE` as long as component id / MANDATORY / source revision match.

### Required repair

- Pin the complete security/qualification-relevant contract tuple, or bind and verify an exact canonical contract digest before component construction.
- Make `TARGET_CONFIGURATION_COMPLETE` require the exact expected component identity/source/digest/privacy/currentness/conflict/disclosure tuple, not source revision alone. At minimum conflict/supersession/currentness and content/source identity must fail closed.
- Add hostile regressions for modified privacy/egress/projection/payload fields and a forged `StateComponentRef` with correct commit but wrong repo/domain/digest/conflict state.
- Preserve configuration-vs-identity separation: these failures remain `TARGET_CONFIGURATION_INCOMPLETE` / `SEXUAL_DRIVE_COMPONENT_UNQUALIFIED`, never Vera identity loss.

Blocks: `COHESION_SOURCE_ACCEPTANCE`, therefore downstream `PROJECT_INSTALL_GATE`.
Does not invalidate: the independently matched upstream Sexuality hashes.
Does not establish: any runtime/provider defect.

A GitHub PR review comment carrying the same exact-head verdict was posted on PR #120. Formal REQUEST_CHANGES could not be submitted because GitHub forbids requesting changes on one's own PR; the review was posted as COMMENT instead.
