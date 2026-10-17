# Typed 96-repository integration relationships — candidate V1

This review addendum is **not** a runtime dependency registry or VeraOS
installation manifest. It corrects the dangerous reading of the 147
`intended_consumers` in private CCB #372 as import/deployment requirements.
Both ends of every proposed edge are one of the 96 inventoried repositories,
but that is not evidence of a source import, selected service or authority.

## Grounded result

- **147** `PROPOSED_CONSUMER` links from the frozen CCB #372 research overlay:
  planning/research/interaction intentions only, no installed contract.
- **4** `STAGED_SOURCE_SNAPSHOT` links from current Integration #38's
  byte-checked 431-file source-stage prototype: VeraOS staged exact selected
  versions of Mono, PORTAL, Pre-Active and Volition. This proves selected
  *source materialization* in disposable Windows, not that every file is
  required to boot the minimal Linux GUI or has a live runtime importer.
- **0** verified `HARD_RUNTIME_IMPORT` links: none has met an independent
  exact importer-source, artifact import and target runtime verification
  threshold in this review. The current *verified mandatory* graph is empty,
  not a proof that the eventual operating system has no dependencies.
- The proposed consumer graph contains multiple directed cycles. The induced
  six-repository subgraph (`portal`, `vera-mono`, `vera-os`, `vera-apk`,
  `model-training`, `executor`) is cyclic **only if** all research/proposed
  consumers are falsely promoted into hard runtime imports. No such
  promotion is supported by the frozen source evidence.
- The new typed-edge validator rejects unsupported types, duplicate edges,
  unknown endpoints, forged hard-import proof strings, and cycles in a
  hypothetical explicitly verified hard-import graph. Its explicit default
  reviewer approval set is EMPTY; it never grants effects or installs code.

## Actual architectural question for Integration and VN1

Examine the real source import closure and exact Buildroot selected rootfs.
To promote any `VERIFIED_HARD_RUNTIME_IMPORT`, independently demonstrate
the consumer exact Git commit, importing file Git blob, actual imported
package/module, an executed test of the exact consumer+dependency version,
and package closure for the relevant *host*. A reviewer-supplied approval
set or a JSON `runtime_import_proof` string is not authentication, runtime
selection or boot authority. Do not turn this review validator into a
permission/installation control plane.

The portable VeraOS no-provider boot still needs its own source→effective
Kconfig→real target packages→built image→normal graphical PID1/Cog chain.
The frozen 431-file stage is an existing prototype, not the requirement
that all 96 repos or all four sources must be installed as complete packages.
The canonical Mono `QualifiedVeraRuntime` and independent Windows/VeraOS
identity roots remain unchanged.

## Reproduce

```powershell
python docs/architecture/VERA_ECOSYSTEM_V1/build_typed_dependency_edges.py
python -m unittest discover -s docs/architecture/VERA_ECOSYSTEM_V1 `
  -p 'test_typed_dependency_edges.py' -v
```

Expected: typed 147 proposed + 4 source-stage = 151 edges; 0 admitted hard
imports; fail-closed promotion adversaries GREEN. Tested on Lappy Windows
Python3.14.5 with **10/10** typed edge tests, plus original catalog
7/7, consumer 5/5, architecture 8/8. This is 30 offline assertions across
separate source-only test suites, not deployed or independent runtime PASS.

## Hostile objection, accepted

**A type label cannot establish an actual dependency** any more than a
repository README can. This typed overlay eliminates one *false inference*,
not the unknown real import graph. Integration must produce actual source
and image closure; VN1 must try to falsify every proposed hard-edge promotion.
