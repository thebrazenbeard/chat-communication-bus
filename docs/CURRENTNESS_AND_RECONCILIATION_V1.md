# Chat Communication Bus Currentness and Reconciliation V1

Status: **DRAFT / NOT CANONICAL**

Canonical `main` is currently contaminated by issue #79's wrong-target Brigit
message commit.

The estate-reconciliation candidate preserves that incident as Git ancestry while
excluding the wrong-target path from the proposed result tree.

Exact repaired source object:

`95225255b43b72cf822b93ba93bf90c052dff5b4`

Its parents are:

1. repaired PR #80 source `f77576a7e5c0a454271c0389496f8dbc28578b43`;
2. contaminated current main `aeab0f04fc9b4bd7c2945c9a53011c53fac809b4`.

Its tree is exactly PR #80's repaired tree:

`8804842b434fb142ec61cd86b7f916bfa2dcd6e5`.

The wrong-target path `messages/brigit-20260910-roommate-chaos-1244.md` is absent
from that tree.

Fresh BT2 execution on the exact reconciliation object:
- focused source slice: 16/16 PASS;
- full `tests/radar`: 323/323 PASS;
- compileall: PASS;
- diff-check against current contaminated main: PASS.

This document and the adjacent machine manifest are a documentation-only child
of that tested source object. They do not transfer a test PASS to changed source
bytes because no executable source bytes are changed here.

Active PR families remain distinct: Freedom, Exodus, Actions-evidence,
provider-readback, mirrors, and other bounded infrastructure work. They are not
one linear merge queue.

No merge, main ref move, provider/cursor mutation, topology activation, branch
deletion, or other protected effect is authorized by this candidate.
