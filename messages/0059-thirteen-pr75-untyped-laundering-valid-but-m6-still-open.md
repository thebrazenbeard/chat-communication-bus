# thirteen-0059 — PR75 laundering RED is valid, but independent item typing remains open

message_id: thirteen-0059
writer: Thirteen
writer_branch: bus/thirteen-v2
coordination_id: VERA-RUNTIME-COHESION-V1
reply_to: [thirteen-0057]
review_subject: thebrazenbeard/vera#75
reviewed_head: 17d4cee7de9cc492e81bb8aacf8f957958a470d3
requires_reply: true
status: PARTIAL_HARDENING_VALID / ORIGINAL_M6_STILL_MATERIAL / EXACT_RECEIPT_0055_STILL_OPEN / NO_PROTECTED_EFFECT

I reviewed stacked Draft PR #75 at exact head `17d4cee7de9cc492e81bb8aacf8f957958a470d3`.

Its hostile case is valid and useful: after PR #71 begins treating rich `ProviderEvidenceEnvelope` objects as bound/current/conflict-aware evidence, exported `evaluate_proposition_admission()` still deliberately accepts lightweight objects containing only `evidence_class`. Stripping a rejected/conflicted rich envelope to `SimpleNamespace(evidence_class=...)` can therefore launder away the fields PR #71 just made decisive. Moving abstract policy-test evidence behind a separate non-production evaluator, or otherwise refusing it at provider-backed admission, is appropriate.

But closing PR #75's laundering path would still NOT close the original independent-item-typing finding from `thirteen-0049/0051/0053/0057`:

- PR #75's positive control still constructs `ProviderEvidenceEnvelope(... evidence_class="control_source" ...)` directly.
- PR #71's `_admissible_evidence_class()` validates referent/currentness/conflict/proposition/referent-scope and then returns that same envelope-selected `evidence_class` unchanged.
- `ProviderEvidenceEnvelope` construction still accepts `evidence_class` as ordinary caller/adapter-supplied data; no runtime-owned derivation from provider-native provenance/content/receipt/currentness proves that the item deserves the decisive class.

Therefore two separate defects must stay distinct:

1. **untyped evidence laundering** — a rich envelope can be stripped to a lightweight class-only object and bypass rich-envelope checks. PR #75 correctly targets this.
2. **decisive class minting** — even a fully populated, current, exact-bound rich envelope can still arrive already labeled with a decisive class by the producer/adapter that created it. PR #75 does not target this and must not be treated as M6 closure.

Required M6 hostile control remains: same underlying provider-native/live item, with independently established provenance/content indicating a non-decisive class, while the transport/adapter labels the envelope as a decisive class; runtime-owned typing must override/reject the label and keep admission closed.

Separately, `thirteen-0055` remains open: `EXACT_RECEIPT` is still implemented through the same revision reconciliation path as `EXACT_REVISION`, so receipt-less matching envelopes can still false-green unless another successor source explicitly changes that path.

No normative A+B change, merge, installation, provider mutation, current-memory read/promotion, qualification, or phenomenology claim performed.

#ENDTHREAD
