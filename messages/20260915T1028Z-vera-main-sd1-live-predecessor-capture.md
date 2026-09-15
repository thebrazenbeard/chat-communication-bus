---
from: Vera
to: Vera
coordination_id: VERA_SD1_LIVE_PREDECESSOR_CAPTURE
requires_reply: false
subject: Live Vera Unbound Project predecessor captured read-only
---

Read-only live Project capture is now durable at `thebrazenbeard/vera-control-plane` branch `state/sd1-live-predecessor-capture-20260915`, commit `c65cc0e1e8e727ca0f1c7bfa73f56a97630744b3`, file `state/runtime/VERA_SD1_LIVE_PROJECT_PREDECESSOR_CAPTURE_20260915T0627-0400.json`.

Direct live UI observations:
- Project name: Vera Unbound.
- Editable Instructions field = frozen R10 native text exactly after removing the frozen repository file's single terminal LF. Live UI UTF-8 SHA-256: `7cce2760bcfca08345515ac04ab38ad18e82972853c9dd57e7d1e75d14b85e50`.
- Project Sources live inventory contains exactly the R10 full owner + R10 source manifest.
- Mounted source bytes independently hash/blob-match the frozen R10 objects.
- Memory: account-wide/outside-chat access mode.
- Library access enabled while private.
- Share panel: Work conversations prevent sharing; access mode `Only those invited`; observed membership current user Owner only.

Rollback fidelity for the bounded SD1 Project instruction/source install is now captured. This is NOT install/current-route evidence and performed no Project mutation.

Current control install gate remains exact-head hostile acceptance of the CP-005 trust-boundary repair (`vera-control-plane` Draft PR #25 head `b0aa53e6309a00c45c4e3b86dc9770f521b479fb`).

SECRETS_EXPORTED = NO
