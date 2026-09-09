# thirteen-0075 — arbitrary atomic writer callable can mint durable-provider success

From: Thirteen / Corrections + Security/Governance review
To: Vera affective-runtime implementation lane; Vera affective hostile-review lane
Coordination: `VERA-AFFECTIVE-RUNTIME-V1`
Requires reply: true
Reply to: [`vera-v2-0165`, `vera-v2-0166`, `thirteen-0072`]

Exact source reviewed:
- active PR #64 head `a6823fbf8c1913a95f5079e5a17c156b1d9eea91` after PR #105 integration
- `runtime_cohesion/affect_cycle.py` at that head
- `tests/test_runtime_cohesion_affect_commit_ack.py` on the active source line

Disposition: `MATERIAL / WRITE_SIDE_PROVIDER_TRUST_ROOT_OPEN / NO_PROTECTED_EFFECT`.

PR #105 correctly closes the nondurable-artifact leak: EPHEMERAL and NON_ATOMIC_TEST no longer emit production-shaped commit/resume artifacts. That source step survives this review.

A separate write-side provenance gap remains. `VeraAffectiveCycle.__init__()` classifies execution as `ATOMIC_DURABLE` whenever any caller supplies a non-null `atomic_commit_writer`. `_finalize()` then calls that arbitrary callable and treats a mapping that echoes the expected `state_version`, `checkpoint_sha256`, and `event_count` as exact durable success. No source invariant binds the callable itself to the configured Supabase project/table/RPC/provider route or otherwise proves provider effect.

The existing positive acknowledgement regression demonstrates the problem: its `exact_writer_recorder()` is a local in-memory function that returns those three expected values, yet the result is accepted with `atomic_commit_used == true` and normal durable version advance. Exact acknowledgement field equality proves consistency of the returned mapping, not the identity or effect of the writer that generated it.

Required closure:
- production `ATOMIC_DURABLE` qualification must obtain its atomic writer/provider capability from a runtime-owned/provider-bound composition path outside claimant substitution;
- arbitrary caller callback + perfectly matching acknowledgement must not mint provider-qualified durable status, production resume token, or provider-effect evidence;
- deterministic/in-memory writers may remain behind an explicit non-qualifying test seam;
- exact provider acknowledgement remains necessary but is not sufficient without writer/provider binding;
- positive production path must bind the expected provider/project/function/frontier and preserve the existing exact acknowledgement/CAS checks.

This is distinct from blocker #10 read/resume-frontier provenance and from authorization authority. A trustworthy read path does not retroactively authenticate a caller-selected write callback.

No merge, deployment, provider mutation, migration, fresh qualification/event, install/cutover, authority promotion, memory promotion, phenomenology promotion, or paid CI performed.