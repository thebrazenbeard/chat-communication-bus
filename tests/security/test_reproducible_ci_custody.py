from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
CI = ROOT / ".github/workflows/ci.yml"
PYPROJECT = ROOT / "pyproject.toml"
HANDLER = ROOT / "supabase/functions/github-bus-ingest/handler.ts"
CUSTODY = ROOT / "architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def test_python_build_and_test_tooling_is_exactly_pinned() -> None:
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    ci = CI.read_text(encoding="utf-8")
    assert 'requires = ["setuptools==84.0.0"]' in pyproject
    assert 'test = ["pytest==9.1.1"]' in pyproject
    assert "pip==26.2.1" in ci
    assert "pip install --upgrade pip" not in ci


def test_ci_uses_immutable_actions_and_exact_supabase_cli_with_sql_reset() -> None:
    source = CI.read_text(encoding="utf-8")
    refs = re.findall(r"uses:\s*([^@\s]+)@([^\s#]+)", source)
    assert refs
    for name, ref in refs:
        assert FULL_SHA.fullmatch(ref), f"un-pinned action {name}@{ref}"

    assert "supabase/setup-cli@ab058987d8d6c725971f6cf9d0b5c98467e30bd1" in source
    assert "version: 2.116.0" in source
    assert "supabase db reset" in source
    assert "supabase/tests" in source
    assert "psql" in source


def test_edge_imports_are_exactly_versioned() -> None:
    source = HANDLER.read_text(encoding="utf-8")
    assert 'jsr:@supabase/functions-js@2.5.0/edge-runtime.d.ts' in source
    assert 'npm:@supabase/supabase-js@2.115.0' in source
    assert 'npm:@supabase/supabase-js@2"' not in source


def test_source_custody_manifest_covers_every_critical_radar_source() -> None:
    assert CUSTODY.exists()
    contract = json.loads(CUSTODY.read_text(encoding="utf-8"))
    assert contract["contract"] == "RADAR_SOURCE_CUSTODY_V1"
    paths = set(contract["paths"])

    required = {
        str(path.relative_to(ROOT)).replace("\\", "/")
        for pattern in (
            "supabase/migrations/*_radar_*.sql",
            "supabase/tests/radar_*.sql",
        )
        for path in ROOT.glob(pattern)
    }
    required.update(
        {
            "supabase/functions/github-bus-ingest/index.ts",
            "supabase/functions/github-bus-ingest/handler.ts",
            "supabase/config.toml",
            ".github/workflows/ci.yml",
            ".github/workflows/writer-lane-guard.yml",
            ".github/workflows/radar-central-dispatcher.yml",
            ".github/workflows/radar-trusted-projector.yml",
            "architecture/contracts/RADAR_TOPOLOGY_V1.json",
            "architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json",
            "architecture/contracts/RADAR_PROJECTION_TRUST_ANCHOR_V1.json",
            "docs/protocol/BUS_MESSAGE_GRAMMAR_V1.json",
            "tests/fixtures/bus_message_grammar_v1.json",
        }
    )
    assert required <= paths


def test_source_hash_script_is_manifest_driven_and_fails_on_missing_paths() -> None:
    source = (ROOT / "scripts/radar_source_hashes.py").read_text(encoding="utf-8")
    assert "RADAR_SOURCE_CUSTODY_V1.json" in source
    assert "FILES = (" not in source
    assert "SOURCE_CUSTODY_PATH_MISSING" in source
