# Radar Anchor E source freeze — 2026-09-09

Status: `SOURCE_ONLY_REVIEW_CANDIDATE / NO_PROTECTED_EFFECT`

## Qualified immutable source being frozen

- source branch at qualification: `radar/reproducible-ci-source-custody-v1-20260906`
- source commit: `dfd3c639d058dcafaa1167e53ad4bdc152d52cf6`
- source tree: `8e51a28db92739d2ce103c72194330dc84a7c415`
- authoritative mode: `LOCAL_NO_PAID_SERVICES`
- qualification run: `34397641413`
- job: `102621180712`
- receipt schema: `2`
- receipt: `PASS`
- canonical validator: `VALID`
- stage-evidence SHA-256: `255409e47204f073cdb4a6b460910364985c2ef6ebff746f61e21622666a445b`
- independent admission: `hephaestus-0062` — `ACCEPT / RECEIPT_ADMISSION / AUTHORITATIVE_QUALIFICATION_PASS / GREEN_ELIGIBLE_UNDER_CONTRACT / NO_PROTECTED_EFFECT`

## Why a successor anchor is required

Historical Anchor D (`401733b2013802880320629a4d8ea06f8bf7b760`) predates the later qualified source repairs for:

- `project_batch` identity/branch protocol binding; and
- atomic claim-bound file projection/journal fencing.

The portable-qualification/OIDC trust design requires the successor anchor to be frozen only after exact authoritative PASS plus receipt admission. That prerequisite is now satisfied for `dfd3c639...`.

## Anchor E rule

`RADAR_PROJECTION_TRUST_ANCHOR_V4.json` freezes the already-qualified projector bytes:

- `projection_anchor_sha = dfd3c639d058dcafaa1167e53ad4bdc152d52cf6`
- `projection_anchor_tree = 8e51a28db92739d2ce103c72194330dc84a7c415`
- `provider_expected_sha_value_at_deploy = dfd3c639d058dcafaa1167e53ad4bdc152d52cf6`

The later metadata/dispatcher commit that records this freeze is **not** the qualified projector SHA and must never be substituted into `RADAR_TRUSTED_PROJECTOR_SHA`.

## Source-only changes

The freeze branch changes only trust/currentness/custody/recovery/test/dispatcher metadata around the already-qualified immutable source target. It does not alter the projector implementation, Edge handler, migrations, or qualified source bytes at `dfd3c639...`.

## Verification ceiling

GitHub compare readback against `dfd3c639...` is the file-scope evidence for this freeze. Private hosted CI runs for this branch terminate with all jobs failed before recorded steps execute; that infrastructure result is not promoted into RED or GREEN test evidence.

No claim is made that the later freeze branch itself has an authoritative qualification receipt. The receipt belongs to the immutable Anchor-E target `dfd3c639... / 8e51a28d...`.

## Protected effects not performed

No merge to `main` or the qualified source branch, Supabase migration application, Edge deployment/configuration, `RADAR_TRUSTED_PROJECTOR_SHA` provider mutation, cursor bootstrap, dispatcher activation on `main`, credential/ruleset/billing change, force-push/history rewrite, native Project mutation, or other protected effect was performed.
