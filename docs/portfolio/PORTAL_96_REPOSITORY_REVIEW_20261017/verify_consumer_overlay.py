"""Offline verification of source-bound 96-repository consumer overlay."""
import json, re, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class ConsumerOverlayTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=json.loads((ROOT/"PORTAL_96_REPOSITORY_ARCHITECTURE_REVIEW_V1.json").read_text(encoding="utf-8"))
  cls.review=json.loads((ROOT/"PORTAL_96_CONSUMER_ADMISSION_OVERLAY_V1.json").read_text(encoding="utf-8"))
  cls.b={x["repository"]:x for x in cls.base["repositories"]}
  cls.c={x["repository"]:x for x in cls.review["repositories"]}
 def test_exact_96_once_and_frozen_source(self):
  self.assertEqual(len(self.c),96)
  self.assertEqual(set(self.c),set(self.b))
  for name,row in self.c.items():
   with self.subTest(name):
    src=self.b[name]
    self.assertEqual(row["default_head"],src["head"])
    self.assertEqual(row["source_tree"],src["tree_sha"])
    self.assertRegex(row["default_head"],"^[0-9a-f]{40}$")
    self.assertEqual(row["source_evidence"]["readme_sha256"],src["readme_sha256"])
 def test_consumers_are_real_repos_not_runtime_claims(self):
  for name,row in self.c.items():
   with self.subTest(name):
    self.assertEqual(len(set(row["intended_consumers"])),len(row["intended_consumers"]))
    self.assertTrue(all(c in self.c and c!=name for c in row["intended_consumers"]))
    self.assertTrue(row["interface_kind"])
    self.assertTrue(row["acceptance_gate"])
    self.assertIn(row["proposed_review_lane"],("PORTAL","INTEGRATION","TRAINING","VN1"))
 def test_runtime_evidence_and_effects_are_never_invented(self):
  for row in self.c.values():
   s=row["runtime_admission"]
   self.assertEqual(s["interface"],"PROPOSED_NOT_INSTALLED")
   self.assertEqual(s["installed"],"UNVERIFIED")
   self.assertEqual(s["selected_route"],"UNVERIFIED")
   self.assertEqual(s["live_consumption"],"UNVERIFIED")
   self.assertEqual(s["verified_behavior"],"NOT_ESTABLISHED")
   self.assertEqual(s["effect_authority"],"NONE_GRANTED")
   self.assertEqual(s["independent_review"],"NOT_ESTABLISHED_BY_THIS_OVERLAY")
 def test_independent_identity_and_private_research_remain_separate(self):
  for name in ("brigit","personification","unbound-sol","orgasm","sexuality","selfimage"):
   self.assertEqual(self.c[name]["intended_consumers"],[])
  for name in ("brigit-unbound","bugops","build-team-2.0","conditioning"):
   self.assertEqual(self.c[name]["intended_consumers"],[])
   self.assertTrue(self.b[name]["archived"])
 def test_no_new_registry_and_mono_is_only_canonical_runtime(self):
  self.assertTrue(self.review["no_new_runtime_registry"])
  self.assertEqual(self.c["vera-mono"]["interface_kind"],"CANONICAL_TASK_EFFECT_ABI")
  for name,row in self.c.items():
   if name!="vera-mono":
    self.assertNotEqual(row["interface_kind"],"CANONICAL_TASK_EFFECT_ABI")
if __name__=="__main__": unittest.main()
