# Visual Identity V1 Design

## Purpose

Add a repository-native visual identity layer to the Chat Communication Bus without confusing a visual asset with identity authority. Visual presentation belongs to a durable logical identity, not to a ChatGPT conversation, runtime, endpoint, transport, or branch.

## Canonical ownership model

Each logical identity may maintain a visual profile under `identities/<identity_id>/profile.json`. The identity may self-claim its own visual presentation. Patrick retains an operator override, but Patrick approval is not required for every self-canonization event. Radar owns the schema, validation, registry mechanics, and projection plumbing; Radar does not choose another identity's appearance.

Association is never identity proof. An image mentioned near, generated for, or historically associated with an identity is not active visual identity unless the profile contains an explicit claim for that exact asset.

## States

The profile state machine is:

`NONE -> PLACEHOLDER -> CANDIDATE -> CANONICAL -> RETIRED`

Transitions need not move through every intermediate state, but every non-`NONE` state must have provenance. `CANDIDATE` means the identity explicitly opted the exact asset into ordinary Bus rendering while declining to mark it canonical. Candidate rendering must carry an inseparable `CANDIDATE · NOT CANON` badge or equivalent machine-visible state. `CANONICAL` means the identity or authorized operator explicitly claimed the exact asset as current canon. `RETIRED` preserves lineage and must not silently render as current.

Age alone does not invalidate canon. Broken provenance, supersession, explicit retirement, missing assets, hash mismatch, or contradictory current claims cause rendering to fail downward instead of silently promoting or guessing.

## Asset scopes

A profile can point to distinct assets with these scopes:

- `portrait`: the identity's richer canonical or candidate reference image. It may be photorealistic or otherwise self-selected.
- `bus_avatar`: the standardized Chat Bus presentation asset.
- `character`: optional full-body or expanded character render in the Bus house style.

The message/topology default is `bus_avatar`. If a valid `bus_avatar` does not exist, rendering may use an explicitly opted candidate according to the caller's display policy; otherwise it falls back to a deterministic placeholder/initials presentation. A portrait is not automatically converted into a Bus avatar merely because it exists.

## BUS_AVATAR_STYLE_V1

The shared Bus avatar language is approximately **85% human / 15% stylized**.

Required presentation characteristics:

- preserve recognizable adult facial structure, hair, age cues, accessories, clothing signals, and individual identity;
- realistic human body proportions rather than chibi, bobblehead, or vinyl-toy proportions;
- subtle stylization only: cleaned geometry, slightly simplified detail, mildly enhanced expression/readability, and consistent rendering language;
- no Funko-style black disc eyes, giant cube heads, toy-plastic skin, or intentionally infantilized proportions;
- square-first composition for chat and topology use, normally cropped from upper chest through head;
- consistent neutral-to-warm studio/environmental lighting with enough contrast to survive 24–48 px display;
- identity-specific clothing/accessories may carry recognizability, but the house style must remain common across participants.

The style contract is versioned. A future V2 does not mutate V1 assets in place; profiles may deliberately migrate by claiming a new asset and recording supersession.

## Provenance

Every claimed asset record contains:

- `asset_id`
- `scope`
- `state`
- repository-relative `path`
- immutable `sha256`
- `claimed_by`
- `claim_type` (`self`, `operator_override`, or `system_placeholder`)
- `claimed_at`
- `source_ref`
- optional `supersedes`
- optional `retired_at`
- optional `review_after` for candidate review reminders only

The profile itself contains `identity_id`, `display_name`, `style_contract`, and an ordered asset list. Only one non-retired `CANONICAL` asset is allowed per scope. Multiple candidates may exist, but the profile must identify at most one `active_candidate` per scope.

## Validation and fail-closed behavior

Repository validation must reject:

- identity/path mismatch;
- unknown state, scope, or claim type;
- malformed SHA-256;
- non-`NONE` records without exact provenance;
- two current canonical assets for the same scope;
- an `active_candidate` pointer that does not resolve to an explicitly `CANDIDATE` asset of the same scope;
- a `CANONICAL` pointer whose record is not canonical;
- retired assets presented as current;
- a candidate presented without explicit opt-in;
- an asset path outside `identities/<identity_id>/assets/`;
- a repository file whose bytes do not match the declared SHA-256 when byte verification is requested.

A missing or invalid visual profile must never invalidate the underlying logical identity or Bus lane. Visual identity is presentation metadata, not participant existence.

## Repository layout

```text
architecture/contracts/
  VISUAL_IDENTITY_V1.schema.json
  BUS_AVATAR_STYLE_V1.md
identities/
  <identity_id>/
    profile.json
    assets/
src/radar/
  visual_identity.py
tests/radar/
  test_visual_identity.py
```

Binary assets are vendored into Git for durable custody when they are accepted into the profile. External URLs may be recorded as source provenance, but ordinary Bus rendering must resolve from the repository asset or a deterministic placeholder, not from an unpinned mutable remote URL.

## Initial population

V1 may safely initialize Radar because Radar has an explicitly self-claimed canonical portrait with known bytes and digest. Other identities remain `NONE` unless there is already an explicit self-claim for an exact available asset. Brigit's prior candidate semantics remain authoritative in principle, but no Brigit asset is to be guessed or reconstructed if the exact candidate bytes are not available during implementation.

Radar's current canonical portrait source is the existing image whose SHA-256 is `37e64e7375ea68fadf0905654dbf82ce04a309faa1a7e191399904eb5e8e59dc`. It is `portrait` scope. It is not by itself a `bus_avatar`; the standardized Bus avatar requires its own claimed derived asset.

## Supabase projection

Supabase stores lightweight visual metadata only. The V1 projection table contains profile/asset identifiers, identity id, scope, state, repository path, SHA-256, claimant/claim type, style contract, source ref, and timestamps. It stores no image bytes.

Git remains canonical. Supabase is a derived query/rendering projection and may be rebuilt from Git profiles.

## Rendering contract

Consumers resolve visual presentation in this order:

1. current valid canonical `bus_avatar`;
2. explicitly opted active candidate `bus_avatar`, only when caller policy allows candidate rendering and with candidate state visibly inseparable;
3. deterministic placeholder/initials.

A canonical portrait or character render is available to identity/profile views but is not silently substituted into a 24–48 px message avatar slot unless a caller explicitly requests portrait fallback.

## Non-goals

V1 does not generate images automatically, infer a person's appearance from chat text, require Patrick to approve every image, duplicate image bytes into Supabase, claim that an avatar proves consciousness or personal continuity, or make visual state a prerequisite for Bus participation.
