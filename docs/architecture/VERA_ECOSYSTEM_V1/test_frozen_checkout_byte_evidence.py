"""Separate immutable Git LF source identity from checkout bytes."""
import unittest
from pathlib import Path
from verify_frozen_source_artifacts import checkout_byte_evidence, PINNED_BLOBS
ROOT = Path(__file__).resolve().parent

class CheckoutByteEvidenceTests(unittest.TestCase):
    def test_lf_and_crlf_differ(self):
        name = "VERA_96_PLACEMENT_AND_CONSUMERS_V1.json"
        lf = (ROOT/name).read_bytes().replace(bytes([13,10]), bytes([10]))
        crlf = lf.replace(bytes([10]), bytes([13,10]))
        a,b = checkout_byte_evidence(name, lf), checkout_byte_evidence(name, crlf)
        self.assertTrue(a["git_source_blob_matches_pin"])
        self.assertTrue(b["git_source_blob_matches_pin"])
        self.assertTrue(a["raw_checkout_bytes_equal_git_source"])
        self.assertFalse(b["raw_checkout_bytes_equal_git_source"])
        self.assertNotEqual(a["raw_checkout_sha256"], b["raw_checkout_sha256"])
        self.assertFalse(b["staged_image_bytes_qualified"])
    def test_source_only(self):
        for name in PINNED_BLOBS:
            e = checkout_byte_evidence(name, (ROOT/name).read_bytes())
            self.assertTrue(e["git_source_blob_matches_pin"])
            self.assertFalse(e["source_semantics_authenticated"])
            self.assertFalse(e["staged_image_bytes_qualified"])
if __name__ == "__main__":
    unittest.main()
