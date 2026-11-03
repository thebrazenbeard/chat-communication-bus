"""Source-only checks for the Supabase Edge bundle observation boundary."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from radar_deployed_source_equivalence import (  # noqa: E402
    InvalidObservation,
    compare_source_files,
)


FILES = ("index.ts", "handler.ts", "provider_503_log.ts", "deno.json")


class SourceEquivalenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "supabase" / "functions" / "github-bus-ingest"
        self.source.mkdir(parents=True)
        self.contents = {name: f"source-{name}\n" for name in FILES}
        for name, content in self.contents.items():
            (self.source / name).write_text(content, encoding="utf-8")
        def git(*args: str) -> str:
            return subprocess.check_output(
                ["git", *args], cwd=self.root, text=True, stderr=subprocess.DEVNULL
            ).strip()
        git("init", "-q")
        git("config", "user.email", "source-only@example.invalid")
        git("config", "user.name", "Source Only Test")
        git("add", "supabase")
        git("commit", "-qm", "source test")
        self.head = git("rev-parse", "HEAD")

    def snapshot(self) -> dict[str, object]:
        return {
            "slug": "github-bus-ingest",
            "status": "ACTIVE",
            "version": 7,
            "verify_jwt": False,
            "ezbr_sha256": "a" * 64,
            "files": [{"name": n, "content": self.contents[n]} for n in FILES],
        }

    def test_exact_byte_parity_remains_hold_without_provider_custody(self) -> None:
        observation = self.snapshot()
        observation["qualified"] = True
        observation["deployment_receipt"] = {"status": "PASS"}
        result = compare_source_files(self.root, self.head, observation)
        self.assertEqual(result["status"], "HOLD")
        self.assertTrue(result["all_files_match"])
        self.assertEqual(result["mismatch_files"], [])
        self.assertEqual(result["evidence_class"], "UNTRUSTED_SOURCE_BYTE_COMPARISON")
        self.assertIn("DEPLOYMENT_CUSTODY_UNVERIFIED", result["reasons"])
        self.assertIn("PROVIDER_BUNDLE_DIGEST_UNBOUND", result["reasons"])
        self.assertIn("DELIVERY_UNVERIFIED", result["reasons"])
        self.assertNotIn("qualified", result)

        forged_digest = self.snapshot()
        forged_digest["ezbr_sha256"] = "f" * 64
        result = compare_source_files(self.root, self.head, forged_digest)
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["provider_bundle_digest_qualified"], False)

    def test_deployed_byte_drift_is_detected_without_echoing_contents(self) -> None:
        observation = self.snapshot()
        observation["files"][1]["content"] = "altered secret-looking body\n"
        result = compare_source_files(self.root, self.head, observation)
        self.assertFalse(result["all_files_match"])
        self.assertEqual(result["mismatch_files"], ["handler.ts"])
        self.assertNotIn("secret-looking", json.dumps(result))

    def test_missing_duplicate_extra_or_untrusted_file_names_fail_closed(self) -> None:
        for altered in (lambda fs: fs.pop(),
                        lambda fs: fs.append(dict(fs[0])),
                        lambda fs: fs.append({"name": "../private", "content": "x"})):
            observation = self.snapshot()
            altered(observation["files"])
            with self.subTest(observation=observation["files"]), self.assertRaises(InvalidObservation):
                compare_source_files(self.root, self.head, observation)

    def test_invalid_metadata_types_and_forged_head_fail_closed(self) -> None:
        for key, value in (("version", True), ("verify_jwt", 0), ("ezbr_sha256", "x")):
            observation = self.snapshot()
            observation[key] = value
            with self.subTest(key=key), self.assertRaises(InvalidObservation):
                compare_source_files(self.root, self.head, observation)
        with self.assertRaises(InvalidObservation):
            compare_source_files(self.root, "b" * 40, self.snapshot())

    def test_dirty_or_symlinked_local_source_is_not_a_trust_anchor(self) -> None:
        path = self.source / "handler.ts"
        path.write_text("dirty", encoding="utf-8")
        with self.assertRaises(InvalidObservation):
            compare_source_files(self.root, self.head, self.snapshot())

    def test_git_assume_unchanged_cannot_forge_committed_source_bytes(self) -> None:
        path = self.source / "handler.ts"
        subprocess.run(
            ["git", "update-index", "--assume-unchanged",
             "supabase/functions/github-bus-ingest/handler.ts"],
            cwd=self.root, check=True, capture_output=True,
        )
        # Git status now lies by omission: the worktree byte mutation is hidden.
        altered = self.snapshot()
        altered["files"][1]["content"] = "UNCOMMITTED_MUTABLE_HANDLER\n"
        path.write_text(altered["files"][1]["content"], encoding="utf-8")
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "--", "supabase/functions/github-bus-ingest"],
            cwd=self.root, text=True,
        )
        self.assertEqual(status, "")
        with self.assertRaises(InvalidObservation):
            compare_source_files(self.root, self.head, altered)

    def test_git_skip_worktree_cannot_forge_committed_source_bytes(self) -> None:
        path = self.source / "handler.ts"
        subprocess.run(
            ["git", "update-index", "--skip-worktree",
             "supabase/functions/github-bus-ingest/handler.ts"],
            cwd=self.root, check=True, capture_output=True,
        )
        altered = self.snapshot()
        altered["files"][1]["content"] = "UNCOMMITTED_MUTABLE_HANDLER\n"
        path.write_text(altered["files"][1]["content"], encoding="utf-8")
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "--", "supabase/functions/github-bus-ingest"],
            cwd=self.root, text=True,
        )
        self.assertEqual(status, "")
        with self.assertRaises(InvalidObservation):
            compare_source_files(self.root, self.head, altered)
        path.unlink()
        path.symlink_to(self.source / "index.ts")
        with self.assertRaises(InvalidObservation):
            compare_source_files(self.root, self.head, self.snapshot())

    def test_cli_reports_hold_for_equal_bytes_and_exit_one_for_drift(self) -> None:
        snapshot_file = self.root / "provider-observation.json"
        executable = ROOT / "scripts" / "radar_deployed_source_equivalence.py"

        def invoke() -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, str(executable), "--source-root", str(self.root),
                 "--expected-head", self.head, "--provider-json", str(snapshot_file)],
                capture_output=True, text=True, check=False,
            )

        snapshot_file.write_text(json.dumps(self.snapshot()), encoding="utf-8")
        exact = invoke()
        self.assertEqual(exact.returncode, 0, exact.stderr)
        self.assertEqual(json.loads(exact.stdout)["status"], "HOLD")

        changed = self.snapshot()
        changed["files"][0]["content"] += "mutation"
        snapshot_file.write_text(json.dumps(changed), encoding="utf-8")
        drift = invoke()
        self.assertEqual(drift.returncode, 1, drift.stderr)
        self.assertEqual(json.loads(drift.stdout)["mismatch_files"], ["index.ts"])


if __name__ == "__main__":
    unittest.main()
