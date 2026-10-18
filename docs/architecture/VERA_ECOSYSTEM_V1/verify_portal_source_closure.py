"""Review-only AST reachability of selected PORTAL Python source.

AST import references are upper-bound SOURCE possibilities, NOT actual
Python import execution, compiled target dependency, or boot requirements.
No application modules are imported and no external code is executed.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


def _module_index(root: Path) -> dict[str, Path]:
    package = root / "portal"
    if not (package / "__init__.py").is_file():
        raise FileNotFoundError("selected PORTAL package is missing")
    files = {}
    for p in sorted(package.rglob("*.py")):
        relative = p.relative_to(root)
        parts = list(relative.parts)
        if parts[-1] == "__init__.py":
            parts.pop()
        else:
            parts[-1] = parts[-1][:-3]
        name = ".".join(parts)
        if name in files:
            raise ValueError("duplicate module path: " + name)
        files[name] = p
    return files


def _references(tree: ast.AST, current: str, is_package: bool,
                known: set[str]) -> tuple[list[tuple[str, int, str]], list[str]]:
    links, unresolved = [], []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "portal" or a.name.startswith("portal."):
                    if a.name not in known:
                        unresolved.append(a.name)
                    else:
                        links.append((a.name, n.lineno, "AST_IMPORT"))
        elif isinstance(n, ast.ImportFrom):
            if n.level:
                anchor = current if is_package else current.rpartition(".")[0]
                parts = anchor.split(".")
                if n.level > len(parts):
                    unresolved.append("relative import escapes PORTAL: " + current)
                    continue
                parent = ".".join(parts[:len(parts)-(n.level-1)])
                base = parent + ("." + n.module if n.module else "")
            else:
                base = n.module or ""
            if not (base == "portal" or base.startswith("portal.")):
                continue
            if base not in known:
                unresolved.append(base)
                continue
            links.append((base, n.lineno, "AST_IMPORT_FROM"))
            for a in n.names:
                candidate = base + "." + a.name
                if candidate in known:
                    links.append((candidate, n.lineno, "AST_IMPORT_MEMBER"))
    return links, unresolved


def inspect_portal_closure(root: Path, resident_path: Path) -> dict:
    """Follow AST-possible imports from actual VeraOS resident + package init."""
    root, resident_path = Path(root), Path(resident_path)
    tree = ast.parse(resident_path.read_text(encoding="utf-8"))
    files = _module_index(root)
    known = set(files)
    direct, missing = _references(tree, "veraos.resident", False, known)
    if missing:
        raise ValueError("unresolved local resident portal import: " + repr(missing))
    seeds = {"portal"} | {target for target, _, _ in direct}
    queued, seen = sorted(seeds), set()
    edges, unresolved = [], []
    while queued:
        module = queued.pop(0)
        if module in seen:
            continue
        seen.add(module)
        path = files[module]
        source = ast.parse(path.read_text(encoding="utf-8"))
        references, missing = _references(
            source, module, path.name == "__init__.py", known)
        unresolved.extend(f"{module}: {x}" for x in missing)
        for target, lineno, kind in references:
            edges.append({"importer_module": module,
                          "importer_file": path.relative_to(root).as_posix(),
                          "importer_blob_sha1": hashlib.sha1(
                            b"blob " + str(path.stat().st_size).encode() + b"\0" +
                            path.read_bytes()).hexdigest(),
                          "line": lineno, "imported_module": target,
                          "evidence_kind": kind})
            if target not in seen:
                queued.append(target)
    if unresolved:
        raise ValueError("unresolved local PORTAL module imports: " + repr(sorted(set(unresolved))))
    records = [{"module": n, "path": files[n].relative_to(root).as_posix(),
                "source_sha256": hashlib.sha256(files[n].read_bytes()).hexdigest()}
               for n in sorted(seen)]
    return {"schema":"VERA_PORTAL_SELECTED_STATIC_IMPORT_CLOSURE_V1",
            "status":"SOURCE_ONLY_AST_IMPORT_REACHABILITY",
            "selected_package":"portal", "direct_resident_imports":sorted(seeds),
            "staged_modules":len(files), "reachable":sorted(seen),
            "modules":records, "edges":sorted(edges,key=lambda e:(
                e["importer_module"],e["line"],e["imported_module"],e["evidence_kind"])),
            "unresolved":[], "verified_runtime_consumption":False,
            "hard_dependency_admitted":False, "buildroot_image_qualified":False}


def summarize(result: dict) -> dict:
    return {"source_only":True,
            "reachable_module_count":len(result["reachable"]),
            "staged_module_count":result["staged_modules"],
            "unreached_module_count":result["staged_modules"]-len(result["reachable"]),
            "buildroot_image_qualified":False,
            "runtime_consumed":False,"hard_boot_requirement":False}


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--component-root",required=True)
    parser.add_argument("--resident",required=True)
    parser.add_argument("--output",required=True)
    a=parser.parse_args()
    result=inspect_portal_closure(Path(a.component_root),Path(a.resident))
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                              encoding="utf-8")
    print(json.dumps(summarize(result),sort_keys=True))


if __name__=="__main__":
    main()
