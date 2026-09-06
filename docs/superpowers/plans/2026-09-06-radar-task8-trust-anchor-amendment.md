# Radar Task 8 trust-anchor execution amendment

Status: binding implementation-plan correction; architecture unchanged.

The original implementation plan contains an impossible sequencing instruction: it says to record the Task-7 journal commit as immutable trust anchor `A`, then create `.github/workflows/radar-trusted-projector.yml` "at A". A commit cannot acquire a workflow after its SHA already exists.

The approved architecture instead requires `A` to contain both the trusted reconciliation source and the reusable trusted-projector workflow, with the dispatcher added only in a later commit that references `A` exactly.

GitHub's reusable-workflow context also requires a correction. The called workflow's ordinary `github` context is associated with the caller workflow, so caller `workflow_sha`/checkout defaults are not proof of the called workflow's immutable source. GitHub OIDC provides `job_workflow_ref` and `job_workflow_sha` specifically for the called reusable workflow.

Correct Task-8 sequence:

1. Task 7 remains a source candidate and is not itself `A`.
2. Add RED supply-chain tests for the reusable workflow.
3. Add the reusable workflow and any trusted bootstrap/CLI source needed by that workflow.
4. The reusable workflow requests a GitHub OIDC token for local self-identification only, without sending it to any provider.
5. It decodes the token payload without logging the token, requires:
   - repository `thebrazenbeard/chat-communication-bus`;
   - exact `job_workflow_ref` path `thebrazenbeard/chat-communication-bus/.github/workflows/radar-trusted-projector.yml@<ref>`;
   - `job_workflow_sha` matching a 40-hex commit SHA;
   - the ref suffix, when it is a raw SHA, equals `job_workflow_sha`.
6. It exposes only the verified `job_workflow_sha` as a step output and checks out `thebrazenbeard/chat-communication-bus` at that exact SHA with `persist-credentials: false`.
7. The reusable workflow never checks out, imports, executes, or consumes actions/scripts/artifacts/caches from a writer branch. Writer branches remain inert Git objects read by trusted code.
8. Commit the reusable workflow plus trusted source. That resulting commit SHA is immutable trust anchor `A`.
9. Only in a successor commit add the default-branch dispatcher, with `jobs.<id>.uses` pinned exactly to `thebrazenbeard/chat-communication-bus/.github/workflows/radar-trusted-projector.yml@A`.
10. Task 9 later uses the same `job_workflow_ref`/`job_workflow_sha=A` claims for provider trust and separately body-binds each provider OIDC request. The self-identification token in Task 8 is never a provider bearer and creates no provider effect.

This amendment preserves the approved trust model and removes the self-reference/caller-context ambiguity. It does not authorize merge, workflow activation on `main`, provider deployment, migration application, credentials changes, or any other protected effect.
