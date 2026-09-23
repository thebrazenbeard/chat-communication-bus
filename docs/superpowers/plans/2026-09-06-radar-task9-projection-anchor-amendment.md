# Radar Task 9 projection-anchor execution amendment

Status: binding implementation-plan correction; approved architecture preserved.

Task 8 froze validate-only trust anchor A at `8cebe395cc12d221ec5627e5492c0ccf15ee801d`. A reusable workflow invoked at A can execute only source contained in A. Therefore Task-9 provider-emission code committed after A cannot become reachable by merely modifying successor files while the dispatcher still pins A.

Task 9 must mint a new immutable **projection trust anchor B** containing the complete provider-capable trusted workflow/source. A remains useful immutable validation evidence and is not rewritten.

Correct sequence:

1. Build body-bound provider request code and Edge verification source on a branch descending from the Task-8 successor.
2. The Edge source must not hardcode B inside B. It reads `RADAR_TRUSTED_PROJECTOR_SHA`, requires exactly 40 lowercase hex characters, and requires OIDC `job_workflow_sha` to equal that configured value. Missing/invalid configuration fails closed. The expected `job_workflow_ref` is constructed from the configured SHA and exact reusable-workflow path.
3. The provider-capable reusable workflow continues to self-resolve its own `job_workflow_sha` from GitHub OIDC, checks out trusted source at that exact SHA, and uses that value as its control-source identity.
4. Every provider HTTP request is serialized once to exact bytes; SHA-256 is computed over those bytes; the request OIDC audience is `chat-communication-bus-supabase:<body_sha256>`; `x-radar-body-sha256` carries the same digest; and the exact same bytes are sent.
5. Edge verification order is binding amendment A4: exact raw bytes -> digest -> GitHub OIDC signature/claims/dynamic audience -> digest header -> durable JTI consume -> JSON/semantic parse -> provider effect.
6. Body/audience/header mismatch must not consume JTI. A cryptographically valid bound but semantically invalid request consumes JTI before returning semantic failure.
7. Commit the complete provider-capable reusable workflow plus trusted source and generic fail-closed Edge source. That resulting SHA is immutable projection trust anchor **B**.
8. In a successor commit only, update the dispatcher pin and `RADAR_TRUST_ANCHOR_V1.json` from A to B, recording A as the predecessor validate-only anchor. The provider deployment configuration, if later authorized, must set `RADAR_TRUSTED_PROJECTOR_SHA=B`.
9. Source completion does not deploy the Edge function, apply migrations, set provider environment, seed provider cursors, or activate the dispatcher on `main`.

A and B are distinct because their executable capabilities differ. Anchor rotation is explicit, append-only source history; no anchor is rewritten.
