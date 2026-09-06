from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
CI = ROOT / ".github/workflows/ci.yml"
PYPROJECT = ROOT / "pyproject.toml"
HANDLER = ROOT / "supabase/functions/github-bus-ingest/handler.ts"
EDGE_DENO = ROOT / "supabase/functions/github-bus-ingest/deno.json"
EDGE_LOCK = ROOT / "supabase/functions/github-bus-ingest/deno.lock"
CUSTODY = ROOT / "architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def test_python_build_and_test_tooling_is_exactly_pinned() -> None:
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    ci = CI.read_text(encoding="utf-8")
    assert 'requires = ["setuptools==84.0.0"]' in pyproject
    assert 'test = ["pytest==9.1.1"]' in pyproject
    assert "pip==26.2.1" in ci
    assert "pip install --upgrade pip" not in ci


def test_ci_uses_only_immutable_actions_and_exact_verification_tools() -> None:
    source = CI.read_text(encoding="utf-8")
    refs = re.findall(r"uses:\s*([^@\s]+)@([^\s#]+)", source)
    assert refs
    for name, ref in refs:
        assert FULL_SHA.fullmatch(ref), f"un-pinned action {name}@{ref}"

    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in source
    assert "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97" in source
    assert "supabase/setup-cli@46f7f98c7f948ad727d22c1e67fab04c223a0520" in source
    assert "version: 2.116.0" in source
    assert "supabase db reset" in source
    assert "supabase/tests/radar_*.sql" in source
    assert "psql" in source

    assert "denoland/setup-deno@22d081ff2d3a40755e97629de92e3bcbfa7cf2ed" in source
    assert "deno-version: 2.9.6" in source
    assert "deno ci" in source
    assert "deno check index.ts" in source


def test_edge_dependency_map_is_exact_and_lock_is_frozen() -> None:
    handler = HANDLER.read_text(encoding="utf-8")
    config = json.loads(EDGE_DENO.read_text(encoding="utf-8"))
    imports = config["imports"]

    assert imports == {
        "jsr:@supabase/functions-js/edge-runtime.d.ts":
            "jsr:@supabase/functions-js@2.5.0/edge-runtime.d.ts",
        "npm:@supabase/supabase-js@2": "npm:@supabase/supabase-js@2.115.0",
    }
    assert 'import "jsr:@supabase/functions-js/edge-runtime.d.ts";' in handler
    assert 'from "npm:@supabase/supabase-js@2"' in handler
    assert config["lock"] == {"path": "./deno.lock", "frozen": True}
    assert config["minimumDependencyAge"] == "P3D"

    assert EDGE_LOCK.exists(), "generated Deno 2.9.6 lock is required"
    lock = json.loads(EDGE_LOCK.read_text(encoding="utf-8"))
    assert lock["version"] == "5"
    assert lock["specifiers"]["jsr:@supabase/functions-js@2.5.0"] == "2.5.0"
    assert lock["specifiers"]["npm:@supabase/supabase-js@2.115.0"] == "2.115.0"
    assert lock["workspace"]["dependencies"] == [
        "jsr:@supabase/functions-js@2.5.0",
        "npm:@supabase/supabase-js@2.115.0",
    ]


def test_source_custody_manifest_covers_dynamic_sql_and_fixed_trust_roots() -> None:
    contract = json.loads(CUSTODY.read_text(encoding="utf-8"))
    assert contract["contract"] == "RADAR_SOURCE_CUSTODY_V1"
    assert contract["version"] == 5
    assert contract["status"] == "SOURCE_ONLY_VERIFICATION_CONTRACT"
    assert set(contract["required_globs"]) == {
        "supabase/migrations/*_radar_*.sql",
        "supabase/tests/radar_*.sql",
    }

    fixed = set(contract["paths"])
    assert {
        "supabase/functions/github-bus-ingest/index.ts",
        "supabase/functions/github-bus-ingest/handler.ts",
        "supabase/functions/github-bus-ingest/deno.json",
        "supabase/functions/github-bus-ingest/deno.lock",
        "supabase/config.toml",
        ".github/workflows/ci.yml",
        ".github/workflows/writer-lane-guard.yml",
        ".github/workflows/radar-central-dispatcher.yml",
        ".github/workflows/radar-trusted-projector.yml",
        "architecture/contracts/RADAR_CURRENT.json",
        "architecture/contracts/RADAR_QUALIFICATION_V1.json",
        "architecture/contracts/RADAR_TOPOLOGY_V1.json",
        "architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json",
        "architecture/contracts/RADAR_TRUST_ANCHOR_V1.json",
        "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V1.json",
        "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V2.json",
        "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V3.json",
        "docs/checkpoints/RADAR_MAIN_DIVERGENCE_RECONCILIATION_2026-09-06.md",
        "docs/operator/RADAR_NO_PAID_QUALIFICATION.md",
        "docs/protocol/BUS_MESSAGE_GRAMMAR_V1.json",
        "tests/fixtures/bus_message_grammar_v1.json",
        "tests/security/test_no_paid_qualification_consistency.py",
        "pyproject.toml",
        "scripts/radar_local_qualify.ps1",
        "scripts/radar_source_hashes.py",
        "scripts/radar_trusted_project.py",
        "scripts/radar_trusted_reconcile.py",
        "src/radar/body_bound_oidc.py",
        "src/radar/central_projection.py",
        "src/radar/github_actions_oidc.py",
        "src/radar/message_grammar.py",
        "src/radar/reconciliation_journal.py",
        "src/radar/trusted_control_snapshot.py",
        "src/radar/trusted_lane_validation.py",
        "src/radar/trusted_reconciler.py",
        "src/radar/trusted_wakeup.py",
        "src/radar/writer_lanes.py",
    } <= fixed

    for pattern in contract["required_globs"]:
        assert any(path.is_file() for path in ROOT.glob(pattern)), pattern


def test_source_hash_script_is_manifest_driven_and_fails_closed() -> None:
    source = (ROOT / "scripts/radar_source_hashes.py").read_text(encoding="utf-8")
    assert "RADAR_SOURCE_CUSTODY_V1.json" in source
    assert "FILES = (" not in source
    assert "required_globs" in source
    assert "SOURCE_CUSTODY_GLOB_EMPTY" in source
    assert "SOURCE_CUSTODY_PATH_MISSING" in source
