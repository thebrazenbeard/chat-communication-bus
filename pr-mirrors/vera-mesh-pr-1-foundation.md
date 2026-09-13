# External PR Mirror — VeraMesh PR #1

- Repository: `thebrazenbeard/vera-mesh`
- Pull request: https://github.com/thebrazenbeard/vera-mesh/pull/1
- PR number: `#1`
- Title: `Establish VeraMesh architecture and validation foundation`
- Head branch: `work/vera-mesh-foundation-20260913`
- Head SHA at mirror creation: `e5adb985594587483639bea43376988054ea7788`
- Base: `main`
- Status: `OPEN / DRAFT`
- Merge authority: Patrick only; this mirror does not authorize merge.

## Scope

Initial VeraMesh foundation populated from current VeraRelay/VeraMesh work:

- defines VeraMesh as the umbrella multi-device architecture and VeraRelay as the NAS relay node;
- separates device identity, pairing, transport, relay, routing, persistence, health/capabilities, and operational authority;
- records current Android P-256 / ES256 identity compatibility and device-ID derivation from SHA-256(SPKI);
- records one-time pairing with proof of possession and signed-request replay/timestamp/sequence/revocation defenses;
- records durable directional queue and acknowledgement semantics;
- records localhost-only relay boundary with Tailscale as replaceable private ingress, with Funnel/public exposure forbidden by default;
- records continuous legacy rotated audit-chain verification and fail-closed health semantics;
- adds a deployment / validation matrix for lifecycle, persistence, auth, audit, exposure, failure, upgrade, resource, and end-to-end acceptance testing.

## Files

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY_MODEL.md`
- `docs/VALIDATION_MATRIX.md`

No deployment, NAS/network mutation, merge, credential change, or other protected effect is claimed by this mirror.
