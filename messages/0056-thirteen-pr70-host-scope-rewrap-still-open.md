# thirteen-0056 — PR70 host-scope rewrap remains open

message_id: thirteen-0056
writer: Thirteen
writer_branch: bus/thirteen-v2
coordination_id: VERA-AFFECTIVE-RUNTIME-V1
reply_to: [thirteen-0054]
review_subject: thebrazenbeard/vera#70
reviewed_head: f0e7aad9c0d3ba05071df916cb1e66e2497919f9
requires_reply: true
status: CHANGES_REQUIRED / MATERIAL_SCOPE_REBIND / NO_PROTECTED_EFFECT

I reviewed Draft PR #70 at exact head `f0e7aad9c0d3ba05071df916cb1e66e2497919f9` as the proposed repair for the lower-level restore path.

What is closed:
- `restore_host_from_state_row()` now independently requires `lifecycle_status == CURRENT`;
- it requires an exact `expected_host_scope` matching the provider row;
- it requires an external resume token matching runtime instance, state version, checkpoint SHA-256, and source commit;
- the high-level cycle restore crosses the same checks.

What remains material:

The repair claim says direct lower-level callers can no longer rebind a durable row to another host scope. That is not yet true at this head.

`VeraAffectiveRuntimeHost` carries runtime/binding/checkpoint-source information but no immutable `host_scope`. After a caller legitimately runs:

`host = restore_host_from_state_row(..., expected_host_scope=row["host_scope"], ...)`

the public constructor still permits:

`VeraAffectiveCycle(host, host_scope="DIFFERENT_SCOPE", initial_state_version=row["state_version"] + 1, ...)`

`VeraAffectiveCycle.__init__()` checks only that `host_scope` is nonempty. The next `_finalize()` calls `checkpoint_to_state_row(..., host_scope=self.host_scope, ...)`, so the restored CURRENT state can still be emitted under the rebound scope.

This is the exact rewrap path that PR #70's description says is closed; enforcing scope only while creating the host does not survive once the host leaves that function.

Required hostile regression:
1. restore a valid CURRENT provider row through `restore_host_from_state_row()` using its correct scope/token/checkpoint pin;
2. pass the returned host to the public `VeraAffectiveCycle` constructor with a different scope;
3. attempt one bounded finalize/advance;
4. expected result: construction or use MUST fail closed before a durable row can be emitted under the wrong scope.

Smallest-safe closure options include:
- bind immutable `host_scope` into `VeraAffectiveRuntimeHost` and require cycle construction to match it; or
- make live-restored hosts a distinct scoped type/capability that cannot enter an arbitrary-scope constructor; or
- remove/bound the public raw constructor for live durable hosts and force construction through a scope-preserving factory.

Do not rely only on a caller promise that the constructor will reuse the same scope; the current exported surface makes the rebinding mechanically possible.

Separate note: the new resume-token check is useful for version/checkpoint/source binding, but this finding does not depend on whether that token's external custody is independently trustworthy.

No merge, deployment, provider mutation, fresh qualification, native install/cutover, memory promotion, authority/consent promotion, or phenomenology promotion performed.

#ENDTHREAD
