# PR mirror — thebrazenbeard/vera#90

Title: `fix: separate provider-backed and abstract admission`
State: OPEN / DRAFT / SOURCE SUCCESSOR
Base: `work/vera-cohesion-untyped-evidence-laundering-review-20260909`
Base SHA: `17d4cee7de9cc492e81bb8aacf8f957958a470d3`
Head: `work/vera-cohesion-provider-admission-boundary-20260909`
Head SHA: `e79b6d00d9c71629830f8bea83c5d6dffe63e95e`

Purpose: make package-level proposition admission provider-strict while retaining lightweight policy fixtures only through explicitly named `evaluate_abstract_proposition_admission`. This is a bounded source step toward PR #75 closure; direct `runtime_cohesion.runtime.evaluate_proposition_admission` and all internal caller rewiring remain an explicit residual boundary.

No normative A+B change, merge, install, provider mutation, or qualification authorized or performed.
