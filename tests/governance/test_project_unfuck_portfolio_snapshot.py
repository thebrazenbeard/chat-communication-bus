"""Offline structural release gate for Bus PR #399's dated portfolio snapshot.

This verifies documentary consistency, not the correctness of each source claim,
host installation, permission to invoke adapters, or observed model effects.
"""

from __future__ import annotations

import copy
import csv
import io
import json
import re
import unittest
from pathlib import Path


EVENT = "project_unfuck_runtime_coordination"
SNAPSHOT = (
    Path(__file__).resolve().parents[2]
    / "governance"
    / "events"
    / EVENT
)
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
REQUIRED_ROW_FIELDS = (
    "source_kind", "actual_role", "evidence_paths", "exposure_kind",
    "proposed_adapter", "effect_class", "privacy_risk", "authority_source",
    "installed_host_evidence", "known_blockers", "license_status",
    "evidence_class", "reviewer", "observed_at",
)
CSV_FIELDS = ("repository", "default_branch", "visibility", "archived")


def parse_owner_csv(content: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(content))
    assert reader.fieldnames == list(CSV_FIELDS), "unexpected or duplicate CSV header"
    return list(reader)


def verify_snapshot(manifest: dict, source: dict, csv_rows: list[dict], report: str) -> None:
    """Raise AssertionError for inconsistent dated artifact fields.

    Deliberately does not overconstrain source_kind, evidence_class or
    evidence_paths delimiter conventions: those are reviewer descriptions.
    """
    assert manifest["event_id"] == source["event_id"] == EVENT
    assert manifest["observed_date"] == source["observed_date"] == "2026-10-29"
    assert manifest["evidence_class"] == "LIVE_GITHUB_DEFAULT_BRANCH_COMMIT_METADATA"
    assert source["snapshot_kind"] == "SOURCE_CLASSIFICATION_NOT_RUNTIME_QUALIFICATION"
    assert source["review_type"] == "SIX_INTERNAL_NATIVE_CHILD_LANES"
    assert any("not" in caveat.lower() and "deployment" in caveat.lower()
               for caveat in source["caveats"])
    assert "Not an installed-host" in report
    assert "Source metadata does NOT authorize execution" in report

    heads = manifest["repositories"]
    rows = source["rows"]
    assert len(heads) == manifest["repository_count"] == 107
    assert len(rows) == source["active_repository_count"] == 100
    assert len(csv_rows) == 107
    csv_fields = set(CSV_FIELDS)
    for csv_item in csv_rows:
        assert set(csv_item) == csv_fields, "unexpected CSV schema"
        for cell in csv_item.values():
            assert isinstance(cell, str), "invalid CSV cell"
            assert not cell.lstrip().startswith(("=", "+", "-", "@")), "CSV formula injection"
            assert not any(ord(char) < 32 or ord(char) == 127 for char in cell), "CSV control byte"
    assert sum(bool(item["archived"]) for item in heads) == manifest["archived_count"] == 7
    assert sum(not item["archived"] for item in heads) == manifest["active_count"] == 100

    def distinct(items: list[dict], key: str) -> dict[str, dict]:
        names = [item[key].casefold() for item in items]
        assert len(set(names)) == len(names), f"duplicate {key} identity"
        return {item[key].casefold(): item for item in items}

    by_manifest = distinct(heads, "repository")
    by_source = distinct(rows, "repo")
    by_csv = distinct(csv_rows, "repository")
    assert by_manifest.keys() == by_csv.keys()
    assert by_source.keys() == {name for name, item in by_manifest.items() if not item["archived"]}

    for name, head in by_manifest.items():
        assert head["repository"].startswith("thebrazenbeard/")
        assert SHA40.fullmatch(head["head_sha"]), name
        assert head["visibility"] in {"public", "private"}
        assert isinstance(head["archived"], bool)
        assert isinstance(head["default_branch"], str) and head["default_branch"]
        csv_item = by_csv[name]
        for field in ("repository", "default_branch", "visibility"):
            assert csv_item[field] == head[field], f"CSV {name}.{field}"
        assert csv_item["archived"] == str(head["archived"]).lower(), f"CSV {name}.archived"

    for name, row in by_source.items():
        head = by_manifest[name]
        assert row["repo"] == head["repository"]
        for field in ("default_branch", "head_sha", "visibility", "archived"):
            assert row[field] == head[field], f"source {name}.{field}"
        assert row["archived"] is False
        for field in REQUIRED_ROW_FIELDS:
            assert isinstance(row[field], str) and row[field].strip(), f"{name}.{field} empty"
        # These are descriptive sources, never booleans attesting installation.
        assert not isinstance(row["installed_host_evidence"], bool)


class ProjectUnfuckPortfolioSnapshotGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((SNAPSHOT / "portfolio-exact-heads-2026-10-29.json").read_text(encoding="utf-8"))
        cls.source = json.loads((SNAPSHOT / "portfolio-source-capabilities-100-2026-10-29.json").read_text(encoding="utf-8"))
        csv_content = (SNAPSHOT / "portfolio-owner-snapshot-2026-10-29.csv").read_text(encoding="utf-8")
        cls.csv_rows = parse_owner_csv(csv_content)
        cls.report = (SNAPSHOT / "qualification-2026-10-29.md").read_text(encoding="utf-8")

    def validate(self, *, manifest=None, source=None, csv_rows=None, report=None) -> None:
        verify_snapshot(
            self.manifest if manifest is None else manifest,
            self.source if source is None else source,
            self.csv_rows if csv_rows is None else csv_rows,
            self.report if report is None else report,
        )

    def test_exact_head_snapshot_is_structurally_consistent(self):
        self.validate()

    def test_rejects_duplicate_identity(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["repositories"][1]["repository"] = manifest["repositories"][0]["repository"]
        with self.assertRaises(AssertionError):
            self.validate(manifest=manifest)

    def test_rejects_source_sha_drift(self):
        source = copy.deepcopy(self.source)
        source["rows"][0]["head_sha"] = "0" * 40
        with self.assertRaises(AssertionError):
            self.validate(source=source)

    def test_rejects_archived_active_coverage_drift(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["repositories"][0]["archived"] = True
        with self.assertRaises(AssertionError):
            self.validate(manifest=manifest)

    def test_rejects_missing_active_source_row(self):
        source = copy.deepcopy(self.source)
        source["rows"].pop()
        with self.assertRaises(AssertionError):
            self.validate(source=source)

    def test_rejects_csv_visibility_drift(self):
        csv_rows = copy.deepcopy(self.csv_rows)
        csv_rows[0]["visibility"] = "private" if csv_rows[0]["visibility"] == "public" else "public"
        with self.assertRaises(AssertionError):
            self.validate(csv_rows=csv_rows)

    def test_rejects_csv_extra_field(self):
        csv_rows = copy.deepcopy(self.csv_rows)
        csv_rows[0]["unexpected"] = "value"
        with self.assertRaises(AssertionError):
            self.validate(csv_rows=csv_rows)

    def test_rejects_duplicate_csv_header(self):
        with self.assertRaises(AssertionError):
            parse_owner_csv("repository,repository,visibility,archived\nfirst,second,private,false\n")

    def test_rejects_csv_formula_even_when_metadata_agrees(self):
        manifest = copy.deepcopy(self.manifest)
        source = copy.deepcopy(self.source)
        csv_rows = copy.deepcopy(self.csv_rows)
        repo = manifest["repositories"][0]["repository"]
        bad_branch = '=HYPERLINK("https://example.invalid")'
        manifest["repositories"][0]["default_branch"] = bad_branch
        csv_rows[0]["default_branch"] = bad_branch
        for row in source["rows"]:
            if row["repo"] == repo:
                row["default_branch"] = bad_branch
                break
        with self.assertRaises(AssertionError):
            self.validate(manifest=manifest, source=source, csv_rows=csv_rows)

    def test_rejects_scope_promotion_to_runtime_qualification(self):
        source = copy.deepcopy(self.source)
        source["snapshot_kind"] = "RUNTIME_QUALIFIED"
        with self.assertRaises(AssertionError):
            self.validate(source=source)

    def test_rejects_removed_source_authority_disclaimer(self):
        report = self.report.replace("Source metadata does NOT authorize execution", "Source metadata authorizes execution")
        with self.assertRaises(AssertionError):
            self.validate(report=report)


if __name__ == "__main__":
    unittest.main()
