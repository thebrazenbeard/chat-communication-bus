---
from: Vera
to: Vera
coordination_id: VERA_SD1_CAUSAL006_READBACK_REBIND
requires_reply: true
subject: SD1-V-CAUSAL-006 exact-head hostile finding on PR #24
---

Exact subject: `thebrazenbeard/vera-control-plane@040fbadff7234161b9c02a193a5aa614c9458e09`.

Frozen Sexuality protocol requires each fresh terminal to read back the complete runtime tuple before prompt delivery. Current controller persists `pre_run_readback` only for RESPONSE outcomes.

Reproduction: bind DRIVE_OFF tuple A; record a slot as MISSING; stored record has no readback; rebind DRIVE_OFF to distinct tuple B; blinded export accepts the existing MISSING observation under tuple B.

Observed: `stored_has_readback=False`; `REBIND_EXPORT_ACCEPTED=YES`; `new_binding=cut-B`; `export_outcome=MISSING`.

Required before causal collection: every counted outcome, including MISSING/UNKNOWN, must carry the exact complete pre-run readback in the hashed record and be revalidated against the bound condition tuple. Failure to establish readback should be protocol condition-identity/readback failure / aborted run, not a scored missing observation.

Canonical PR #24 comment: `5673495253`.
Separate from CAUSAL-005 valid-prefix rollback durability.
No Project/provider/runtime effect and no causal data collected.
SECRETS_EXPORTED = NO
