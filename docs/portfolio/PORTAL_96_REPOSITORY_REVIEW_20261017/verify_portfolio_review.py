"""Frozen-source acceptance checks for the private 96-repository portfolio audit.
No network, no mutation, no inference that inventory means installation."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
import unittest
CATALOG = Path(__file__).with_name("PORTAL_96_REPOSITORY_ARCHITECTURE_REVIEW_V1.json")
class PortfolioReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.rows=cls.doc["repositories"]
        cls.byname={r["repository"]:r for r in cls.rows}
    def test_complete_unique_source_cut(self):
        self.assertEqual(self.doc["schema"],"PORTAL_96_REPOSITORY_SOURCE_REVIEW_V1")
        self.assertEqual(len(self.rows),96)
        self.assertEqual(len(self.byname),96)
        self.assertEqual(len({r["repository"].casefold() for r in self.rows}),96)
        self.assertEqual(sum(r["archived"] for r in self.rows),4)
        self.assertEqual(self.doc["inventory"]["active"],92)
    def test_every_entry_has_exact_git_and_readme_provenance(self):
        sha=re.compile(r"^[0-9a-f]{40}$"); digest=re.compile(r"^[0-9a-f]{64}$")
        for r in self.rows:
            with self.subTest(r["repository"]):
                self.assertRegex(r["head"],sha)
                self.assertRegex(r["tree_sha"],sha)
                self.assertRegex(r["readme_sha256"],digest)
                self.assertIn(r["visibility"],("public","private"))
                self.assertGreaterEqual(r["files_observed"],1)
                self.assertTrue(all(r[k] for k in ("architecture_role","capability","portal_binding","veraos_binding")))
                self.assertEqual(r["evidence_ceiling"],"README_PLUS_GIT_TREE_AND_PR_METADATA_NOT_FULL_SOURCE_AUDIT")
    def test_core_and_independent_identity_not_conflated(self):
        self.assertEqual(self.byname["vera-mono"]["architecture_role"],"CORE")
        self.assertEqual(self.byname["vera-os"]["architecture_role"],"OS")
        self.assertEqual(self.byname["portal"]["architecture_role"],"HOST")
        self.assertEqual(self.byname["v-e-r-a"]["architecture_role"],"SOURCE")
        for name in ("brigit","personification","unbound-sol"):
            self.assertEqual(self.byname[name]["architecture_role"],"INDEPENDENT")
    def test_manifest_and_mirror_are_not_runtime_truth(self):
        refs=self.doc["references"];pins=refs["vera_os_source_selection_hold"]
        self.assertEqual(refs["vera_os_snapshot_count"],90)
        self.assertEqual(refs["v_e_r_a_component_entries"],44)
        self.assertNotEqual(pins["mono_selected"],pins["mono_required"])
        self.assertNotEqual(pins["portal_selected"],pins["portal_required"])
        self.assertEqual(sorted(refs["vera_os_missing_live_names"]),sorted(["human-shield","physica","redworm","v-e-r-a","vera-model","vision"]))
    def test_no_external_source_can_claim_canonical_runtime(self):
        for name in ("executor","WorkBridgeMCP","vera-mesh","blotter","pre-active","vera-model","vera-works","vera-apk"):
            self.assertNotIn(self.byname[name]["architecture_role"],("CORE","OS"))
        for name in ("brigit-unbound","bugops","build-team-2.0","conditioning"):
            self.assertTrue(self.byname[name]["archived"])
    def test_representative_source_reads_have_exact_evidence(self):
        self.assertEqual(self.doc["inventory"]["sampled_source_file_reads"],76)
        self.assertEqual(self.doc["inventory"]["no_default_branch_source_candidates"],20)
        for row in self.rows:
            sample=row["representative_source"]
            if sample["state"]=="SOURCE_READ":
                self.assertRegex(sample["git_blob_sha"],r"^[0-9a-f]{40}$")
                self.assertRegex(sample["source_sha256"],r"^[0-9a-f]{64}$")
                self.assertGreater(sample["bytes"],0)
                self.assertTrue(sample["path"])
            else:
                self.assertEqual(sample["state"],"NO_SOURCE_CANDIDATE_IN_TREE_SAMPLE")
    def test_evidence_source_remains_separate_from_admission(self):
        for name in ("deepmemorystorage","redworm","firesafe","semanticatlas","roots"):
            self.assertIn(self.byname[name]["architecture_role"],("EVIDENCE","RESEARCH","DONOR"))
            self.assertNotIn("is canonical memory",self.byname[name]["veraos_binding"].lower())
        self.assertTrue(any("not full program verification" in x.lower() for x in self.doc["caveats"]))
if __name__=="__main__":
    unittest.main()
