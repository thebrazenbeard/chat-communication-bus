# VeraOS selected PORTAL component/import closure — 2026-10-17

**Status:** independently reproduced Lappy *source-stage review* on PORTAL-owned
noncolliding private Draft. NOT a verified Linux package closure, guest image,
boot requirement, runtime selection, installed service or effect authority.

## Immutable inputs

- Owner VeraOS #38 at `c6837f6c2a357cc5fa5cec5836e79cb3d9dc4fb7`
  retains selected source prototype: Mono 316 + PORTAL 89 + Pre-Active 18 +
  Volition 8 = 431 source files. Actual local staged receipt SHA256:
  `6f0031c1fcbaed41e4e3f6947e90a92ed5656ac3e09329de7d8e0b0f8417eca5`.
- The exact staged PORTAL checkout is
  `thebrazenbeard/portal@36fa04da4e5eb383fecf463c72a43b94ca47d7e5`,
  as confirmed by `git rev-parse HEAD`; resident source from the earlier
  pinned VeraOS #38 checkout
  `beef4a6d6e6339e4da8bc89702b1f1882c1fb968`.
  Resident imported module behavior must be rechecked if #38 changes.
- No code or import of the PORTAL-owned full Windows Desktop/Project Runner
  service was authorized or executed. The scanner uses `ast.parse`, not
  Python import/exec. It does not assert which import paths execute in a
  target Linux interpreter.

## Concrete static source relationships

1. VeraOS `src/veraos/resident.py` references
   `portal.vera_task_handoff`. Python package initialization means
   `portal/__init__.py` is another potential import entrypoint.
2. PORTAL `portal/__init__.py` contains **14 module-level**
   `from .module import symbol` links, including host_bridge, host_pump,
   runtime, discovery, coordinator, task_currentness and route_resolver.
   That is a stronger source import issue than a portfolio donor edge, but
   not evidence that their processes execute or must boot on Linux.
3. AST upper-bound traversal across selected `portal/portal` package found
   **43 staged package Python modules**, **19 reachable**, **24 not reached**,
   and **47 typed import references**. The full PORTAL staged source set
   contains 89 Python files including runner/auxiliary files not in this
   43-module package audit. Absence from AST traversal is NOT evidence a
   module is safe to remove: dynamic imports, resource access, conditional
   imports and optional features need separate test/target closure.
4. The machine-reviewed report `PORTAL_SELECTED_IMPORT_CLOSURE_20261017.json`
   records line-level importer paths, module names, staged raw-byte SHA and
   AST evidence. Status is explicitly SOURCE_ONLY, not HARD_RUNTIME_IMPORT.

## Critical reproducibility distinction

A Windows Git checkout with `core.autocrlf=true` has CRLF bytes for selected
`portal/__init__.py`, whereas Git's immutable tree object has LF bytes.
Concrete original file: 107 CRLF line endings in a 2856-byte staged file.
`git hash-object --no-filters <stage>` and raw file SHA differ from
`git -C <checkout> ls-tree HEAD portal/__init__.py`; normal filtered
`git hash-object <stage>` matches the committed Git object.

The provenance script verified **19/19 reachable modules** byte-identical
to their selected Windows checkout and **19/19 raw byte-mismatches** against
committed immutable Git blob SHA. This DOES NOT establish corruption or an
unqualified image: content remains semantically equivalent under line-ending
normalization, and the source stage receipt is a checkout-byte receipt.
It DOES establish that *checkout byte equality* and *committed Git-object
byte equality* must never be treated as the same evidence claim.
A Linux Buildroot materialization can have different source bytes/receipt
unless clone checkout attributes and byte materialization are fixed and
independently verified. Only a real target image receipt can establish
packaged target member bytes.

## Hostile review and owner decision

> CHALLENGE (accepted): 19 source AST-reachable modules do not prove the
> minimum boot requirement. A dynamic path or import conditional may require
> additional source even when the static graph is smaller.

> CHALLENGE (accepted): raw staging bytes that do not match Git object bytes
> undermine a claim of reproducibility *from the immutable Git tree*,
> even when staged files faithfully copy the Windows checkout. Clarify the
> intended byte authority; don't silently normalize or delete source.

**Integration #38 owner requested:** validate the actual 89 selected source
and PORTAL `__init__` import side effects under target Python, decide whether
the current four-source resident needs a lean portal task-handoff entrypoint
without eagerly importing unrelated host modules, and pin explicit source
materialization/EOL policy before real image comparison. No PORTAL code
change should be cherry-picked by assumption.

**VN1 independent reviewer requested:** rerun on isolated exact checkout,
challenge AST under-approximation and import-time side effects, check CRLF
versus immutable blobs and target system imports. A forged source receipt
must never qualify an image.

**Training cognitive owner:** Mono-only no-provider TASK_OPENED/HELD/cold
recovery #109 proves core capability without Pre-Active/Volition, not that
present VeraOS resident can omit its four staged sources.

## Reproduction

```powershell
python -m unittest discover -s docs/architecture/VERA_ECOSYSTEM_V1 -p 'test_portal_*py' -q
python docs/architecture/VERA_ECOSYSTEM_V1/verify_portal_source_closure.py `
  --component-root <staged-components/portal> --resident <veraos/resident.py> `
  --output <source-closure-json>
python docs/architecture/VERA_ECOSYSTEM_V1/audit_selected_portal_git_materialization.py `
  --checkout <pinned-portal-source-checkout> --stage <staged-components/portal> `
  --closure-json <source-closure-json> `
  --expected-head 36fa04da4e5eb383fecf463c72a43b94ca47d7e5 `
  --output <stage-materialization-json>
```

Source scan eight tests + provenance four tests = **12/12 PASS** on Lappy
Python 3.14.5, after intentional missing-module RED and Git-object mismatch
RED were corrected. No QEMU, new host process, model, task/effect, production
state, user private memory or canonical install.
