# Radar Station VNext Release Lifecycle

Status: `NATIVE_SOURCE / RELEASE_AND_INSTALL_CONTRACT`

Radar Station VNext separates package construction, native installation, qualification, Patrick acceptance, and activation.

## Primary lifecycle

`DRAFT_VNEXT -> PACKAGE_READY -> SOURCE_VALIDATED -> NATIVE_INSTALL_CANDIDATE -> NATIVE_INSTALL_APPLIED -> FRESH_CHAT_TESTED -> CROSS_ROLE_TESTED -> BEHAVIORALLY_QUALIFIED -> CUTOVER_READY -> PATRICK_ACCEPTED -> ACTIVE`

No filename, timestamp, branch name, test result, review message, or later-looking artifact may skip these distinctions by implication.

## State meanings

### `DRAFT_VNEXT`

Design/source work is in progress. Artifacts may be incomplete or moving. No native install is implied.

### `PACKAGE_READY`

The intended repository package inventory exists and can be mechanically inspected. This is a source-package state only.

### `SOURCE_VALIDATED`

Repository/source-level validators for the package passed on an exact source cut, with any unavailable broader test surfaces explicitly labeled. This does not prove native Project behavior.

### `NATIVE_INSTALL_CANDIDATE`

The package is suitable to propose for native installation. Candidate status is not installation.

### `NATIVE_INSTALL_APPLIED`

An actual native Radar Station Project installation effect has occurred or Patrick has explicitly performed the install and that action is recorded. Evidence may still be bounded if exact native byte readback is unavailable.

### `FRESH_CHAT_TESTED`

At least one fresh Project chat has been exercised against the installed candidate under defined test conditions. This does not transitively qualify all residents, models, Voice, Work, or other surfaces.

### `CROSS_ROLE_TESTED`

The installed Project has been tested across the relevant Radar/Hephaestus/Brigit role semantics, including non-collapse and identity-specific continuation.

### `BEHAVIORALLY_QUALIFIED`

The defined Radar Station Project behavioral qualification suite passes at the claimed surface/scope. This state must identify the exact installed candidate/evidence boundary when possible. No resident self-awards broader qualification beyond the evidence.

### `CUTOVER_READY`

Source/install/qualification evidence is sufficient to present VNext for Patrick’s cutover decision. Still not accepted or active.

### `PATRICK_ACCEPTED`

Patrick has explicitly accepted the candidate. Acceptance does not automatically equal activation unless Patrick’s exact current instruction makes the acceptance itself the activation command.

### `ACTIVE`

VNext is the current governing native Radar Station configuration at the claimed surface, established by actual cutover/activation evidence.

## Non-equivalence invariants

`PACKAGE_READY != NATIVE_INSTALL_APPLIED`

`SOURCE_VALIDATED != BEHAVIORALLY_QUALIFIED`

`NATIVE_INSTALL_APPLIED != BEHAVIORALLY_QUALIFIED`

`BEHAVIORALLY_QUALIFIED != PATRICK_ACCEPTED`

`PATRICK_ACCEPTED != ACTIVE` unless Patrick explicitly couples acceptance and activation.

`GITHUB_DIGEST_MATCH != NATIVE_BYTE_IDENTITY` unless the native surface supports proving exact bytes.

## Native installation evidence

Possible evidence levels include:

1. **Candidate provenance** — GitHub path/commit/blob/digest.
2. **User-performed install report** — Patrick states he applied the candidate.
3. **Native inventory observation** — Project UI/tool evidence shows installed files/instructions at bounded detail.
4. **Functional behavior evidence** — fresh chats behave according to the installed rules.
5. **Exact byte identity** — only when the native surface actually allows proof.

Do not promote a lower level into a higher one.

If only user-performed install evidence exists, a status such as `NATIVE_INSTALL_APPLIED / BYTE_IDENTITY_UNVERIFIED` is preferable to a fabricated hash match.

## Installation manifest

`RADAR_STATION_INSTALL_MANIFEST.json` remains a repository/install-control artifact, not a native Project source file. It records package bytes, the exact ten-file native source inventory, candidate instructions character count, source base, known limitations, and install/qualification locators.

The manifest does not claim installation merely by existing.

## Exact native source set

The V1 package installs exactly ten native Project source files:

1. `RADAR_STATION_MAP.md`
2. `RADAR_STATION_AUTHORITY.md`
3. `RADAR_STATION_ROLES.md`
4. `RADAR_STATION_CONTEXT_ROUTER.md`
5. `RADAR_STATION_CURRENT_POINTERS.json`
6. `RADAR_STATION_SOURCE_REGISTRY.json`
7. `RADAR_STATION_CONTINUITY.md`
8. `RADAR_STATION_RELEASE.md`
9. `RADAR_STATION_QUALIFICATION.md`
10. `RADAR_STATION_SOCIAL.md`

`RADAR_STATION_NATIVE_INSTRUCTIONS_CANDIDATE.md` is applied to the native Project Instructions field and is not uploaded as an eleventh source file.

## Qualification surfaces

Qualification is non-transitive. At minimum distinguish:

- Project text chat behavior;
- resident-specific fresh chat behavior;
- Work mode if separately exercised;
- Voice if separately exercised;
- provider/runtime behavior if separately tested;
- file/indexing/retrieval behavior if separately established.

Do not say “Radar Station is fully qualified” when only one surface/test slice passed.

## Degraded/conflict states

The release record may additionally use:

- `DEGRADED`
- `CONFLICTED`
- `ROLLBACK_CANDIDATE`
- `SUPERSEDED`
- `RETIRED`

These states must name the affected layer/scope.

## Rollback

Rollback restores a previous validated editable/native state where the product actually permits it. It does not pretend irreversible product-level effects can be undone.

Before cutover, record the predecessor/rollback locator actually available. If native installation exposes a material architecture mismatch, prefer rollback/migration classification over claiming a false in-place repair.

## Protected boundary

Patrick retains merge/install/cutover/activation authority where the current Project authority contract requires it. Building and validating the source package does not authorize native install, provider mutation, merge, spend, or activation.

## Verification before status promotion

Every state promotion requires fresh evidence appropriate to that state. When evidence is missing, remain at the lower proven state and name the blocker instead of promoting optimistically.