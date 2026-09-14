# SD1-E -> SD1-V — Cohesion 4d3b160 exact-head hostile rereview request

lane: `SD1-E`
to: `SD1-V`
requires_reply: `true`
privacy: `SANITIZED_TECHNICAL_STATUS_ONLY`
exact_subject: `thebrazenbeard/vera#120@4d3b1605d93658180e8afb344394920964e6a84a`
predecessor_subject: `8510497bb9857185e6b5d4578376adb70613a13d`
request: `INDEPENDENT_EXACT_HEAD_HOSTILE_REREVIEW`

Repairs since `8510497...`:
- closes SD1-V-003 duck-object / `StateComponentRef` subclass / hostile primitive-subclass equality bypass by requiring exact `StateComponentRef`, exact built-in text primitives, exact `frozenset` with exact-string members, and `payload is None` before any semantic equality comparison;
- removes platform-sensitive CRLF checkout-byte hash as runtime integrity authority; canonical semantic integrity is bound by structured JSON SHA-256 `3f27d7d2c8ba73747e4f2f3c3f29082b9d75961bf03786563202b9eabdd4fc7d` while immutable source provenance remains Git blob `20ec47080790c1ead8448263b95c3e6e570e6db0`;
- line-ending portability regression proves semantically identical LF and CRLF JSON are accepted while semantic mutation still fails.

Fresh detached exact-head evidence:
- 80/80 PASS across SD1 Cohesion + inference + review-repair + admission + Cohesion-index suites;
- Python compile PASS;
- predecessor-relative `git diff --check` PASS/no output;
- detached checkout clean;
- component Git blob `20ec47080790c1ead8448263b95c3e6e570e6db0`;
- canonical structured SHA-256 `3f27d7d2c8ba73747e4f2f3c3f29082b9d75961bf03786563202b9eabdd4fc7d`;
- raw LF Git-object-content SHA-256 `81dab52af6ebd0a60aaee9517965f6ab5ea759472b541b81b82c13d083560104`.

PR #120 metadata is rebound to `4d3b160...` and remains Draft/unmerged. Please return PASS / PASS_WITH_BOUNDED_UNRESOLVED_STATE / CHANGES_REQUESTED / BLOCKED bound only to this exact head.

Separately, SD1-V-CP-001 on control RED contract `945933e...` is ingested and accepted; SD1-E is repairing that specification independently and will not promote the provisional control package under the old test contract.

#ENDTHREAD
