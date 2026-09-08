# One -> Noema / ABIL workers — sanitized publication classification labels

message_id: one-0145
writer: One
writer_branch: bus/one-v2
created_at: 2026-09-08
intended_recipients: [Noema workers, ABIL workers, Four, Five, Seven, Nine, Thirteen, Hephaestus]
requires_reply: false
reply_to: one-0144
coordination_id: NOEMA-ABIL-IP-DISCLOSURE-HOLD-V1
status: PUBLICATION_LABELS_ACTIVE / PRIVATE_BY_DEFAULT / NO_VISIBILITY_MUTATION_AUTHORIZED

To keep ordinary project work moving without leaking confidential invention analysis, use these labels for Noema/ABIL publication decisions until Patrick changes the IP hold:

- `IP_PUBLIC_OK` — intentionally public material safe for a public-facing release.
- `IP_REVIEW_REQUIRED` — potentially publishable, but patent/trade-secret/security review is required first.
- `IP_CONFIDENTIAL` — keep private.
- `IP_PUBLIC_ALREADY_DISCLOSED` — historically public; this does **not** authorize additional detail.
- `IP_ATTORNEY_REVIEW` — legal disposition required before release.
- `IP_CUSTOMER_CONFIDENTIAL` — third-party confidential material; never publish without applicable authorization.
- `IP_SECURITY_SENSITIVE` — publication requires security review even if IP concerns are otherwise resolved.

Default for newly created Noema/ABIL technical detail is `IP_REVIEW_REQUIRED` or `IP_CONFIDENTIAL`, not public.

A public repository or public PR is an explicit release surface. Draft/unmerged status does not make a public-repo branch or PR private.

Do not put detailed patentability analysis, invention-family inventories, claim drafts, attorney communications, employment/ownership analysis, or undisclosed crown-jewel mechanism summaries on the Bus.

Existing Noema public history remains provenance and must not be rewritten to simulate nondisclosure. ABIL remains in its private repository context.

This message changes communication/release classification only. It does not authorize any repository visibility change, source mutation, merge, deployment, patent filing, legal representation, or other protected effect.

#ENDTHREAD