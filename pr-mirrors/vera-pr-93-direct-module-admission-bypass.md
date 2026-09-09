# PR mirror — thebrazenbeard/vera#93

Title: `review: seal direct runtime admission bypass`
State: OPEN / DRAFT / TEST-ONLY HOSTILE SUCCESSOR
Base: `work/vera-cohesion-provider-admission-boundary-20260909`
Base SHA: `e79b6d00d9c71629830f8bea83c5d6dffe63e95e`
Head: `work/vera-cohesion-direct-module-admission-bypass-review-20260909`
Head SHA: `20cac95f4d29572e99ac2a4eaca83b4c3fd5867e`

Purpose: pin PR #90's explicit residual. Direct `runtime_cohesion.runtime.evaluate_proposition_admission` must be provider-strict, while lightweight policy-fixture behavior remains available only through an explicitly named `evaluate_abstract_proposition_admission`. The RED also keeps exact current `ProviderEvidenceEnvelope` admission working at the direct module boundary.

No normative A+B change, merge, install, provider mutation, qualification, or paid CI action authorized or performed.
