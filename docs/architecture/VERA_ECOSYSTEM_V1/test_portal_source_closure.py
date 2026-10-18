"""Hostile static import-closure tests; no package import or guest boot."""
import json
import tempfile
import unittest
from pathlib import Path
from verify_portal_source_closure import inspect_portal_closure, summarize

class SelectedPortalImports(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        p=self.root/"portal"
        p.mkdir()
        (p/"__init__.py").write_text("from .dispatch import resolve\n")
        (p/"dispatch.py").write_text("from .support import token\n")
        (p/"support.py").write_text("token = 'ok'\n")
        (p/"handoff.py").write_text("from .dispatch import resolve\n")
        (p/"orphan.py").write_text("import portal.ghost\n")
        self.resident=self.root/"resident.py"
        self.resident.write_text("def main():\n    from portal.handoff import unused\n")
    def test_package_initialization_is_a_real_static_import_seam(self):
        rows=inspect_portal_closure(self.root,self.resident)
        self.assertEqual(set(rows["reachable"]),{"portal","portal.handoff","portal.dispatch","portal.support"})
        self.assertNotIn("portal.orphan",rows["reachable"])
        self.assertEqual(rows["status"],"SOURCE_ONLY_AST_IMPORT_REACHABILITY")
        self.assertEqual(rows["unresolved"],[])
    def test_eager_package_initialization_reaches_unrelated_to_requested_symbol(self):
        (self.root/"portal"/"handoff.py").write_text("VALUE = 1\n")
        rows=inspect_portal_closure(self.root,self.resident)
        self.assertIn("portal.dispatch",rows["reachable"])
        self.assertIn("portal.support",rows["reachable"])
    def test_fails_closed_on_missing_relative_local_import(self):
        (self.root/"portal"/"dispatch.py").write_text("from .missing import never\n")
        with self.assertRaisesRegex(ValueError,"unresolved local"):
            inspect_portal_closure(self.root,self.resident)
    def test_does_not_call_imported_python_module_or_effect(self):
        (self.root/"portal"/"dispatch.py").write_text("raise RuntimeError('never execute')\n")
        rows=inspect_portal_closure(self.root,self.resident)
        self.assertIn("portal.dispatch",rows["reachable"])
    def test_absolute_import_and_relative_import_are_distinct_and_typed(self):
        (self.root/"portal"/"handoff.py").write_text("import portal.support\n")
        rows=inspect_portal_closure(self.root,self.resident)
        self.assertTrue(any(x["importer_module"]=="portal.handoff" and x["imported_module"]=="portal.support" for x in rows["edges"]))
        self.assertEqual(rows["verified_runtime_consumption"],False)
        self.assertEqual(rows["hard_dependency_admitted"],False)
    def test_summary_stays_source_evidence_not_guest_requirement(self):
        rows=inspect_portal_closure(self.root,self.resident)
        s=summarize(rows)
        self.assertEqual(s["source_only"],True)
        self.assertEqual(s["buildroot_image_qualified"],False)
        self.assertLessEqual(s["reachable_module_count"],s["staged_module_count"])
    def test_importer_git_blob_matches_actual_git_object(self):
        import hashlib
        rows=inspect_portal_closure(self.root,self.resident)
        record=next(e for e in rows['edges'] if e['importer_module']=='portal')
        blob=(self.root/'portal'/'__init__.py').read_bytes()
        expected=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
        self.assertEqual(record['importer_blob_sha1'],expected)
    def test_invalid_resident_file_fails_explicitly(self):
        with self.assertRaises(FileNotFoundError):
            inspect_portal_closure(self.root,self.root/"missing-resident.py")
if __name__=="__main__":
    unittest.main()
