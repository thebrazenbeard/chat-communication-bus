# PR mirror — thebrazenbeard/vera#117 / R3 admission requirement-class repair

State: OPEN / DRAFT / STACKED HOSTILE-REVIEW REPAIR / UNMERGED

Exact repair tuple:
- reviewed R3 source parent: `thebrazenbeard/vera@fc9e747e69313c3da74183d605b96ae20f4523b5`
- Vera PR: `#117`
- repair head: `51009ecd8052b86aee01742af2ade1abc2db6bbf`
- target/base branch: `work/vera-cohesion-r3-inference-boundary-20260911` (PR #116 line)
- changed paths: `runtime_cohesion/inference_boundary.py`, `tests/test_inference_boundary.py`

Hostile-review finding:
`bind_admitted_state()` trusted caller `mandatory_component_ids` without cross-binding it to each included component's declared `requirement_class`. A declared `MANDATORY` component could therefore be silently downgraded, and a declared `OPTIONAL` component could be silently upgraded.

Repair:
- included `MANDATORY` components must also be mandatory in the admission policy input;
- included `OPTIONAL` components may not be promoted to mandatory by that input;
- existing missing-mandatory and optional-omission fail-closed behavior remains.

Verification on the exact repair branch:
- `python -m unittest tests.test_inference_boundary tests.test_inference_boundary_architecture` -> `Ran 53 tests ... OK`
- `python -m compileall -q runtime_cohesion tests` -> exit 0 / quiet
- `git diff --check HEAD^ HEAD` -> exit 0

The regressions were observed RED before the corresponding source repairs (`ValueError not raised`). Test count includes inherited `unittest` cases and is not a unique-requirements count.

This mirror records source work only. No merge, install/cutover, provider mutation, paid execution, canonical-memory promotion, provider-currentness promotion, behavioral qualification, or phenomenology promotion is authorized or implied.
