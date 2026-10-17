"""Stdlib checks reject accidental promotion of review into deployment."""
import copy
import json
import unittest
from pathlib import Path
from verify_architecture_source_contracts import check_architecture, _gitblob_sha

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/"VERA_96_PLACEMENT_AND_CONSUMERS_V1.json").read_text(encoding="utf-8"))
BOM=json.loads((ROOT/"VERAOS_MINIMAL_BOM_V1.json").read_text(encoding="utf-8"))
class ArchitectureCandidateTests(unittest.TestCase):
 def test_architecture_source_manifest(self):
  self.assertEqual(check_architecture()["rows"],96)
 def test_exact_96_and_no_selected_runtime(self):
  self.assertEqual(len(DATA["repositories"]),96)
  self.assertTrue(all(x["runtime_admission"]["installed"]=="UNVERIFIED"
      and x["runtime_admission"]["effect_authority"]=="NONE_GRANTED"
      and x["runtime_evidence"]=="NOT_ESTABLISHED_BY_THIS_DOCUMENT"
      for x in DATA["repositories"]))
 def test_embedded_donors_never_sibling_imports(self):
  self.assertFalse(any(x["sibling_repo_import_required"] for x in DATA["repositories"]))
  self.assertEqual(DATA["canonical_runtime"],"vera_core.QualifiedVeraRuntime")
 def test_independent_private_archive_exclusions(self):
  rows={x["repository"]:x for x in DATA["repositories"]}
  for n in ("brigit","personification","unbound-sol","orgasm","sexuality","selfimage",
            "brigit-unbound","bugops","build-team-2.0","conditioning"):
   self.assertNotIn(rows[n]["placement_proposal"],
     ("VERAOS_BOOT_REQUIRED","VERAOS_STAGED_SOURCE"))
 def test_rootfs_source_manifest_matches_exact_431(self):
  self.assertEqual(sum(x["files"] for x in BOM["staged_sources"]),431)
  self.assertEqual([x["repo"] for x in BOM["staged_sources"]],
    ["vera-mono","portal","pre-active","volition"])
  self.assertEqual(BOM["status"],"PROPOSED_NOT_BUILT")
 def test_guest_acceptance_never_promoted(self):
  gates={x["gate"]:x["status"] for x in BOM["acceptance"]}
  self.assertEqual(gates["KCONFIG"],"UNQUALIFIED")
  self.assertEqual(gates["IMAGE"],"NOT_BUILT")
  self.assertEqual(gates["NORMAL_GUI"],"NOT_BOOTED")
  self.assertEqual(gates["COLD_TWO_BOOT"],"NOT_RUN")
  self.assertEqual(gates["MODEL"],"HOLD")
  self.assertFalse(BOM["image_produces_authority"])
 def test_no_network_dependency_for_boot(self):
  self.assertFalse(BOM["platform"]["network_required"])
  self.assertIn("GitHub",BOM["excluded_boot_dependencies"])
  self.assertIn("model weights",BOM["excluded_boot_dependencies"])
 def test_git_blob_sha_function_matches_protocol(self):
  sample=b"opaque local sample"
  import hashlib
  expected=hashlib.sha1(b"blob 19\0"+sample).hexdigest()
  self.assertEqual(_gitblob_sha(sample),expected)
if __name__=="__main__": unittest.main()
