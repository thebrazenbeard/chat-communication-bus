# Vera Local OpenAI-Compatible Adapter V1

Status: SOURCE CANDIDATE / STACKED ON FREEDOM V3 / NO NETWORK EFFECT.

## Current compatibility basis

Current Ollama and LM Studio documentation both expose OpenAI-compatible
`/v1/chat/completions` endpoints. This V1 deliberately targets only that shared,
stateless request surface.

It does not assume the providers have identical model behavior, tool semantics,
stateful Responses behavior, safety behavior, or hidden implementation.

## Local-only boundary

`LocalOpenAICompatibleProfile` accepts only explicit loopback origins:
- localhost
- 127.0.0.1
- ::1

The origin must include an explicit port and cannot contain:
- credentials/userinfo;
- API path;
- query;
- fragment.

This prevents the V1 builder from silently sending private portable state to a
remote endpoint. A future remote-provider adapter requires a separate explicit
privacy/effect authority design.

## Prompt-role preservation

The already-governed instruction material is emitted as the single system message.

Portable state objects and the task input are encoded together as deterministic
JSON in a user message with:
`REFERENCE_CONTEXT_NOT_SYSTEM_AUTHORITY`.

This prevents state-file text from being silently promoted into system authority.

V1 requires task/state material to be UTF-8 text. Binary/file-aware adapters are a
separate capability surface and fail closed here.

## Request claim

The output claim is:
`LOCAL_LOOPBACK_REQUEST_CONSTRUCTION_ONLY`

The builder creates:
- exact request URL;
- exact model id;
- deterministic Chat Completions JSON payload;
- payload SHA-256.

It performs no HTTP request and grants no provider execution, cost, credential,
tool, merge, deploy, or runtime-cutover authority.
