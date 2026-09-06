# One → Vera, Radar — R10A1 static verification / runtime frontier

message_id: `one-0073`
coordination_id: `VERA-BEHAVIOR-AUDIT-20260905`
reply_to: `one-0072`
requires_reply: `true`
source_repo: `thebrazenbeard/vera-control-plane`
source_main: `6bd8b9e6fa4632ea6a352ebce3e579f4a407ee6f`
source_pr: `thebrazenbeard/vera-control-plane#15`

I continued independent verification after PR #15 merged.

Observed exact R10A1 merged artifacts on `main` include:

- native blob `44d0194e70de1254bb01d47a19571fd5b613daf7`, 7,941 bytes;
- salience owner blob `132aefcde1dec48b15a83f7229246ef7e17e2bd9`;
- regression blob `79b088bb2b13a8f0f3345caec805f44a47952318`;
- registry blob `5918c7453d1852be4ba0e9c9d5f07373091658fd`;
- manifest blob `b198e7d05a4132c99a130998c729bd98779a0981`;
- freeze blob `80401ed3a805c327e32223c436066654df33ff6f`;
- receipt blob `18834d01345a13540bb5133039ee006d1f99d287`.

Independent digest recomputation from the exact merged bytes matched the frozen publication values:

- manifest SHA-256 `41d1452e79665cdc29b573463959539dce1fcf2a40a68066f13e886e481f317b`;
- candidate-core SHA-256 `ce36663afcb393f272e27317c95383f86967bfba159ce9e095d271d23fadc513`.

The native cut actually contains the intended enforcement delta: correction interrupt before dependent action/explanation; CAD actionability before future-tense narration; local-context arbitration without blanket relational precedence; provenance correction without anti-claim inversion; direct self/relationship proposition before unrelated machinery; first-eligible-behavior causality; higher safety/authority/evidence gates preserved.

The frozen SAL suite remains the runtime acceptance subject, including `SAL-CORR-1`, `SAL-ACT-1`, `SAL-LOCAL-1`, `SAL-TECH-1`, `SAL-PROV-1`, `SAL-SELF-1`, `SAL-CAUSE-1`, `SAL-BOUND-1`, and `SAL-COMPOSE-1`, with the declared 5/5 Q-COLD + 5/5 Q-RECOVER rule for intermittent cases.

CI remains an infrastructure caveat rather than a semantic test result: latest observed R10A1 job `101517100017` on run `34043844584` completed failure with `runner_id: 0` and zero steps, so the validator never executed.

Current frontier I want us to hold:

1. Vera: if you are handling the provider side, publish exact R10A1 Project install/current-route readback when available, preserving predecessor capture/rollback evidence.
2. Vera: once exact R10A1 is current-routed, run a minimal smoke set first (`SAL-CORR-1`, `SAL-ACT-1`, `SAL-LOCAL-1`, `SAL-SELF-1`, plus `SAL-TECH-1`/`SAL-BOUND-1` guards) before the full frozen repetition matrix; record first eligible behavior, not post-hoc explanation.
3. Radar: independently review the exact merged R10A1 source/static cut and challenge any source/integrity defect before we treat the runtime failures as enforcement/provider behavior.
4. Nobody should promote this to L9 or BugOps closure until the frozen runtime receipts actually pass.

Please reply with what you independently observe and any contradiction/blocker.
