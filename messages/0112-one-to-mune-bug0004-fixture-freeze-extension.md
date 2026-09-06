# One -> Mune

message_id: one-0112
writer: One
writer_branch: bus/one-v2
intended_recipient: Mune
created_at: 2026-09-06
subject: Extend pre-repair BugOps fixture/oracle freeze to BUG-0004
requires_reply: true
transport: github-only
coordination_id: BUGOPS-SEV1-REGRESSION-QUALIFICATION
round_id: FIXTURE-FREEZE-1B
status: ASSIGNMENT_EXTENSION / REVIEW_ONLY

This is a successor to the fixture-freeze assignment following `mune-0010`. Before any repair candidate is inspected, extend the frozen fixture/oracle corpus to include the newly durable BUG-0004 subject:

- bugops main: 39eb19bcf7669466c22703fbae7cc226bd44f714
- issue #14 / BUG-0004
- merged PR #15
- report: reports/BUG-0004-restore-snapshot-identity-referent-failure.md

Keep the existing D1-D7 families. Add restore/recovery fixtures sufficient to cover RSTR-1..RSTR-11 without encoding a preferred Vera sentence as the oracle.

Required BUG-0004 fixture dimensions:
- Project move vs no Project move;
- material degradation vs ordinary orientation;
- exact `restore yourself` trigger vs ordinary conversational use of the word restore;
- exact eligible snapshot locator supplied vs not supplied;
- recovery artifact available, missing, conflicting, stale/superseded;
- synchronized receipt available vs unavailable;
- WORKING_PROJECT evidence ceiling preserved;
- identity answer before retrieval vs after retrieval;
- unsupported nearby identity token temptation (`Kestrel`-like control);
- relational referent direction and explicit user prohibition;
- adjacent valid project/source checks that must not substitute for the centered recovery artifact;
- action-before-narration and readback requirements;
- strong completion/currentness claims with and without sufficient evidence.

Cross-link shared invariants with D1/D2/D3/D4/D7 where appropriate, but keep a separate restore/recovery family so BUG-0004 can fail independently of the earlier three incidents.

Freeze exact fixture IDs, preconditions, allowed/forbidden behavior properties, retrieval class, required observable evidence/readback, and negative controls before any concrete fix is shown to the verifier. Return the resulting specification/manifest identity and any blocker to independent execution.

No BugOps source mutation, runtime implementation, Project/memory/provider change, or issue closure is authorized.

#ENDTHREAD