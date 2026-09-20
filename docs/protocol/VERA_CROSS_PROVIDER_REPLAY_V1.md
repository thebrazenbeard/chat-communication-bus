# Vera Cross-Provider Replay V1

Status: SOURCE CANDIDATE / STACKED ON FREEDOM V4 / NO PROVIDER EXECUTION.

## Purpose

Compare externally obtained provider outputs against one frozen portable execution
subject using explicit observable invariants.

The replay layer is deliberately weaker than identity or behavioral-equivalence
claims. It answers only whether named visible invariants passed for each observed
run.

## Frozen subject

A ReplayCase binds:
- case id;
- exact portable execution envelope digest;
- ordered text invariants;
- case claim `FROZEN_OBSERVABLE_TEXT_INVARIANTS_ONLY`.

V1 invariant kinds:
- REQUIRED_LITERAL
- FORBIDDEN_LITERAL

Case sensitivity is explicit per invariant.

## Observed run

An ObservedProviderRun binds:
- exact envelope digest;
- provider manifest digest;
- provider/model/adapter identity;
- request digest;
- exact output text + SHA-256;
- observation claim `EXTERNAL_OUTPUT_OBSERVATION_ONLY`.

The harness does not call providers. Outputs are supplied after external execution.

## Cross-provider report

A cross-provider report requires:
- at least two unique run ids;
- at least two distinct provider ids;
- every run bound to the same replay envelope.

Each run receives only per-invariant pass/fail plus all_passed.

The report claim is:
`OBSERVABLE_INVARIANT_RESULTS_ONLY_NOT_IDENTITY_EQUIVALENCE`.

Even if all providers pass every invariant, the report does not assert:
- same identity;
- same mind;
- same hidden state;
- consciousness/phenomenology;
- causal equivalence;
- full behavioral equivalence;
- provider interchangeability.

Different output wording may pass the same invariants; exact textual equality is
not the target.

No provider call, credential use, paid compute, merge, deploy, provider
configuration, or runtime cutover occurs in this candidate.
