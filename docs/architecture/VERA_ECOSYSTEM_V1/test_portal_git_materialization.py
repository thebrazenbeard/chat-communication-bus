"""Git source byte vs checkout/stage byte conformance, disposable repos."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from audit_selected_portal_git_materialization import verify


def git(root,*args):
    x=subprocess.run(["git","-C",str(root),*args],capture_output=True,
                     text=True,timeout=15,shell=False,check=True)
    return x.stdout.strip()


class SelectedGitMaterializationTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        self.checkout=self.root/"checkout"
        self.stage=self.root/"stage"
        for x in (self.checkout,self.stage): (x/"portal").mkdir(parents=True)
        git(self.checkout,"init","-q")
        git(self.checkout,"config","user.name","offline-test")
        git(self.checkout,"config","user.email","offline-test@invalid.local")
        self.relative="portal/__init__.py"
        self.closure={"modules":[{"path":self.relative}]}
    def committed(self,bytes_value:bytes,autocrlf:str="false"):
        git(self.checkout,"config","core.autocrlf",autocrlf)
        (self.checkout/self.relative).write_bytes(bytes_value)
        git(self.checkout,"add",self.relative)
        git(self.checkout,"commit","-q","-m","fixture")
        shutil.copyfile(self.checkout/self.relative,self.stage/self.relative)
        return git(self.checkout,"rev-parse","HEAD")
    def test_unconverted_source_bytes_match_commit_blob(self):
        head=self.committed(b"VALUE = 1\n")
        evidence=verify(self.checkout,self.stage,self.closure,head)
        self.assertTrue(evidence["stage_equals_git_blob_all"])
        self.assertEqual(evidence["staged_modules_checked"],1)
    def test_crlf_checkout_matches_stage_but_not_committed_blob(self):
        head=self.committed(b"VALUE = 1\r\n",autocrlf="true")
        evidence=verify(self.checkout,self.stage,self.closure,head)
        self.assertTrue(evidence["stage_equals_checkout_all"])
        self.assertFalse(evidence["stage_equals_git_blob_all"])
        self.assertEqual(evidence["not_same_as_committed_git_blob"],[self.relative])
    def test_mismatching_checkout_stage_fails_closed(self):
        head=self.committed(b"VALUE = 1\n")
        (self.stage/self.relative).write_bytes(b"VALUE = 2\n")
        with self.assertRaisesRegex(ValueError,"stage differs"):
            verify(self.checkout,self.stage,self.closure,head)
    def test_wrong_exact_source_commit_rejected(self):
        head=self.committed(b"VALUE = 1\n")
        with self.assertRaisesRegex(ValueError,"HEAD not selected"):
            verify(self.checkout,self.stage,self.closure,"a"*40)


if __name__=="__main__":unittest.main()
