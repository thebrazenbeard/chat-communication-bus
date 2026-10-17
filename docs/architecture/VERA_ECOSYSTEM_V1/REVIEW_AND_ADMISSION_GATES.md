# Architecture V1 unresolved decisions and peer review requests

These are **requests**, not authenticated Integration/Training/VN1 approvals.
Each reviewer must fresh-read source heads and post an exact bounded disposition
to Bus #368. A PR comment alone is not live runtime evidence or deployment authority.

## Integration (L1/L2), VeraOS/Mono owner
- Challenge the four-component source stage (Mono/selected PORTAL/Pre-Active/
  Volition), target Python/ELF, PID1, DRM/Cog fonts/input, state directory and
  offline boot requirements. Identify any actual missing build package and
  the smallest exact test for it. Is 431 a frozen source count but NOT
  reliable proposed build count? Correct the distinction if so.
- Compare Mono #77, PORTAL A1 #55 and resident OS #38: which task/locator/
  source/CAS/recovery contracts are truly equal; which host identity and state
  roots intentionally differ? No shared live SQLite migration without approval.
  **Specific actual source discrepancy:** OS38 `handle_text` defaults to
  `conversation_id='veraos-local-console'`, while Desktop A1 requires an
  explicit client locator. Decide whether that OS-only implicit local-console
  scope is legitimate, and how external Cog clients are prevented from
  accidentally collapsing into one conversation.
  **Specific response difference:** no-provider OS38 returns `status=BLOCKED`
  after `TASK_OPENED`, whereas Desktop A1 returns `state=HELD` and an
  underlying `PENDING_NO_ADMITTED_PROVIDER` status. Define an explicit typed
  portable projection without changing Mono's internal task events.
  **Lifecycle question:** OS38 `ResidentHandles.close()` closes Pre-Active's
  store, not visibly the canonical runtime task/state handles. Confirm
  actual owned resource closure with executable target-compatible tests.
- Provide API names, immutable selected source heads, test commands, actual
  status SOURCE/STAGED/BUILT/TARGET_RUNTIME/GUI, with no false promotion.
- Existing #38 ext2 member audit source is not real image-byte proof; request
  actual Kconfig/config/hash/real debugfs plan with resource/authority gates.

## Training (L2/L3), cognitive admission owner
- Challenge whether Pre-Active and Volition must be in every offline image,
  or whether a minimal Mono-only no-provider HELD resident is safer.
- Can the proposed task→provider/source→result contract express exact session,
  loaded model bytes, nonce and one DONE/route without authorizing effects?
- Keep Rezon guarded adoption REJECTED pending independent source-origin proof;
  preserve actual #106/#107 measurements (not appealing names).
- Bound Qwen/GLM placement to 32GiB RAM + RTX3050 4GiB VRAM, distinguish
  physical capacity from currently free memory and real loaded-model results.

## VN1 (L3/L4), independent challenger
- Falsify a proposed repo placement with observed source and counterexample;
  inspect all 96 and particularly industrial/vehicle, sensory, private,
  independent identities and archives. The script verifies *structure*,
  not whether an assignment is correct.
- Re-run the exact-source verifier independently, reject forged blob matches,
  and test a mutated placement/BOM with false `INSTALLED` or `IMAGE_PASS`
  assertions. A GitHub blob presence test is not runtime conformance.
- Compare A1 Win32 venv launcher PID mismatch, #55 true cold task recovery,
  #56 fake CLAIMED wave no-effect, OS #38 ext2 fake-debugfs vs actual image,
  and upstream #32 VirtIO 8193+ completed-frame overflow.
- Return a source-test to boot-test gap matrix, preserving all red gates.

## PORTAL and Codex sequencing
- PORTAL should first reconcile owner objections and freeze a V1 *candidate*
  interface decision; do not decide by majority of PR comments or infer an
  authenticated reviewer ACK. Review readiness is separate from merge.
- Single existing Codex conversation may be handed a *new* bounded
  representative source-conformance implementation only after PORTAL has
  accepted A1 owner returns and closed the documented Win32 cold-test PID
  harness flaw (or isolated it as an exact owner test follow-up).
- Do not ask Codex to copy 96 repos into VeraOS or build a parallel task
  authority. One code packet / isolated branch / positive+adversarial tests.
- Patrick exact separate authority remains required for image build/QEMU,
  model load, deployment, disk install, provider trust, paid compute or memory.

## Architecture gate before calling V1 accepted
1. Exactly 96 provenance-bound dispositions without automatic installation.
2. Agreed Mono task/effect contracts and no duplicate control plane.
3. Agreed normal VeraOS minimal rootfs bill of materials and what runs remote.
4. One executable source-level cross-host equivalence slice with real tests;
   *runtime-level* acceptance stays pending until a host/guest is observed.
5. Integration/Training/VN1 have separately reviewed exact frozen code and
   explicitly resolved or carried forward their strongest objections.
