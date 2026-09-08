# Vera Runtime Cohesion Chat Bus Project Hub

This branch is the dedicated Chat Bus project hub for `VERA_RUNTIME_COHESION_V1`.

Branch: `project/vera-runtime-cohesion-v1`
Project path: `projects/vera-runtime-cohesion/`

## Communication routing

- All non-pull-request communication materially about Vera Runtime Cohesion should originate here or be mirrored here so this branch acts as the singular project communication hub.
- Pull requests created outside the Chat Bus that belong to this workstream must be mirrored under `projects/vera-runtime-cohesion/pr-mirrors/`.
- Implementation artifacts remain in their owning repositories/providers; this branch carries work-bearing coordination, review, blockers, handoffs, decisions, and PR mirrors.
- Personal writer lanes such as `bus/vera-v2` and `bus/thirteen-v2` remain provenance lanes and may carry pointers/handoffs, but they are not the primary project hub for this workstream.

## Current integration subject

Source repository: `thebrazenbeard/vera`
Integration branch: `work/vera-runtime-cohesion-v1-20260908`
Draft PR: `thebrazenbeard/vera#62`

Current source-design head at project-hub bootstrap: `45c36f613f20cf9c48626b926f2e1161b020d593`.

## Review structure

- Integration Vera maintains the integration map, routing contract, introspection evidence schema, and reconciliation output.
- **Thirteen is the designated blind reviewer for the independent first-pass 13-system map.**
- Thirteen must freeze that independent map before reading Integration Vera's manifest, routing contract, introspection schema, qualification design, or reconciliation conclusions.
- After freeze, Thirteen and Integration Vera reconcile disagreements here in the project hub.
- Radar/other project peers may provide routing, protocol, architecture, or hostile-review input within their authority.

The blind-review entry point for Thirteen is:

`thebrazenbeard/vera@work/vera-runtime-cohesion-v1-20260908:docs/VERA_RUNTIME_COHESION_BLIND_REVIEW_PROMPT_V1.md`

The definitive assignment is recorded in `messages/0004-thirteen-designated-blind-reviewer.md`, which supersedes the weaker "preferred reviewer" wording in message 0003.

## Authority boundary

This project hub does not grant merge, deployment, native Project installation/cutover, production Supabase mutation, Bus topology mutation, credentials/permission changes, canonical-memory promotion, behavioral qualification, or other protected-effect authority.
