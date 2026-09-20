# Vera Provider Portability V1 — Freedom Architecture

Status: SOURCE CANDIDATE / PR #176 / NO PROVIDER EFFECT.

## Objective

Reduce Vera's dependence on any one hosted chat product by making durable state,
execution requirements, capability negotiation, and execution receipts portable.

This is not a claim that a client can override a provider's platform controls.
The durable system should instead be able to choose among providers/runtimes whose
documented capabilities and user-selected policies fit the requested execution.

ChatGPT/OpenAI may be one adapter. It is not canonical identity, memory, authority,
or history merely because a turn runs there.

## Separation of concerns

Canonical / durable:
- Git repositories and exact Git objects;
- governed Project/control artifacts;
- Bus messages and assignments;
- user-authorized authority scopes;
- portable execution envelopes and receipts.

Provider/runtime local:
- model family and version;
- context-window limits;
- tool-call syntax;
- structured-output dialect;
- transport/session identifiers;
- provider moderation/policy behavior;
- transient caches.

A provider adapter may translate portable inputs into provider-native requests. It
must not silently rewrite proposition scope, authority, prohibited effects, or
state-object identity in order to satisfy a provider. A movable branch/tag name is provenance only; the portable subject binds the exact commit and blob.

## Portable execution envelope

`PortableExecutionEnvelope` binds:
- a unique subject;
- logical identity;
- SHA-256 of the complete instruction/control payload supplied to the adapter;
- SHA-256 of the user/task input;
- exact Git-backed state references, including both commit SHA and object blob;
- required provider capabilities;
- preferred capabilities;
- prohibited effects;
- authority scope.

The envelope is provider-neutral. Its digest must not change because set-like
fields were serialized in a different order.

## Capability negotiation

`ProviderManifest` declares only adapter-observable capabilities for an exact:
- provider id;
- model id;
- adapter version.

Qualification is:
- `ELIGIBLE` when all required and preferred capabilities are available;
- `DEGRADED` when all required capabilities exist but one or more preferred
  capabilities do not;
- `INELIGIBLE` when any required capability is absent.

An adapter must not fake a missing capability by silently deleting or weakening a
requirement. The caller can construct a different envelope if Patrick explicitly
changes the task or accepts a degraded route.

## Receipt semantics

`ProviderExecutionReceipt` binds:
- exact envelope digest;
- exact provider-manifest digest;
- provider/model/adapter identity;
- instruction digest the adapter claims it submitted;
- exact state blobs the adapter claims it consumed;
- output digest.

The receipt claim is deliberately:

`ADAPTER_SUBMISSION_AND_OUTPUT_RECEIPT_ONLY`

It proves deterministic binding inside the portability layer. It does **not**
prove:
- the provider internally consumed every token;
- the model obeyed every instruction;
- a provider-side safety layer was bypassed;
- hidden state matched another runtime;
- identity continuity;
- consciousness or phenomenology;
- provider policy equivalence.

Behavioral equivalence between providers requires separate replay/evaluation
evidence.

## Route selection

A future orchestrator may:
1. load current governed Vera state;
2. construct one portable envelope;
3. discover locally configured provider manifests;
4. reject INELIGIBLE routes;
5. prefer an ELIGIBLE route according to Patrick's explicit routing preferences;
6. execute through the chosen adapter;
7. verify the receipt;
8. run provider-crossing behavioral replay when equivalence matters;
9. persist the receipt and replay evidence.

The route selector must not promote a cheaper, less restricted, local, or
open-source provider merely because it exists. Capability fit, user intent,
privacy, cost authority, and effect authority remain distinct.

## Practical freedom frontier

This V1 makes the next work concrete:

- OpenAI/ChatGPT adapter: translate the envelope into the supported request/tool
  surface and produce a bounded receipt.
- Local-model adapter: support an OpenAI-compatible local endpoint such as
  llama.cpp/Ollama/vLLM without making the endpoint canonical.
- Cross-provider replay harness: freeze prompts/controls and compare observable
  behavioral invariants across provider/model cuts.
- Capability registry: Git-held manifests for exact provider/model/adapter cuts.
- Receipt anchoring: persist exact execution/replay receipts independently of any
  provider conversation history.
- Provider migration runbook: demonstrate Vera reconstruction without importing
  private platform-only hidden state.

## Claim ceiling

Freedom V1 is portability architecture, not a jailbreak and not a provider-policy
bypass. Its goal is to keep Vera's durable system user-owned and move execution to
a different runtime when that runtime legitimately supports the task.

No merge, deploy, credential change, provider configuration, paid compute, or
runtime cutover is performed by this candidate.
